import datetime as dt
import json
import os
import shutil
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request, send_file

from schedules import human, merge_station_configs


DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
BYDAY = {"mon": "MO", "tue": "TU", "wed": "WE", "thu": "TH", "fri": "FR", "sat": "SA", "sun": "SU"}


def _slot(raw):
    if isinstance(raw, list):
        return raw[0], raw[1], "", 0, 0
    return (raw.get("start", "00:00"), raw.get("end", "23:59"), raw.get("title", ""),
            int(raw.get("pre", 0) or 0), int(raw.get("post", 0) or 0))


def calendar_text(stations, recurring=True):
    today = dt.datetime.now()
    monday = (today - dt.timedelta(days=today.weekday())).date()
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "PRODID:-//Internet Radio Recorder//2.2.0//PL", "X-WR-CALNAME:Internet Radio Recorder"]
    for station in stations:
        if not station.get("enabled", True):
            continue
        for day, items in (station.get("schedule") or {}).items():
            if day not in DAYS or not isinstance(items, list):
                continue
            for raw in items:
                start, end, title, pre, post = _slot(raw)
                date = monday + dt.timedelta(days=DAYS[day])
                sh, sm = map(int, start.split(":")); eh, em = map(int, end.split(":"))
                starts = dt.datetime.combine(date, dt.time(sh, sm)) - dt.timedelta(minutes=pre)
                ends = dt.datetime.combine(date, dt.time(eh, em)) + dt.timedelta(minutes=post)
                if ends <= starts:
                    ends += dt.timedelta(days=1)
                uid = f"{station.get('name', '')}-{day}-{start}-{title}".replace(" ", "_").replace("@", "_")
                summary = (title or "Nagranie").replace("\n", " ").replace(",", "\\,")
                description = f"Stacja: {station.get('name', '')} | Ramówka: {start}-{end} | pre {pre} min / post {post} min".replace(",", "\\,")
                lines += ["BEGIN:VEVENT", f"UID:{uid}@internet-radio-recorder",
                          f"DTSTART:{starts:%Y%m%dT%H%M%S}", f"DTEND:{ends:%Y%m%dT%H%M%S}"]
                if recurring:
                    lines.append(f"RRULE:FREQ=WEEKLY;BYDAY={BYDAY[day]}")
                lines += [f"SUMMARY:📻 {summary}", f"DESCRIPTION:{description}", "END:VEVENT"]
    return "\r\n".join(lines + ["END:VCALENDAR"]) + "\r\n"


def create_app(load, save, state, lock, ensure, test_stream, root, config_root=Path("/config")):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    root = Path(root).resolve()
    config_root = Path(config_root)

    def media_path(relative):
        candidate = (root / str(relative)).resolve()
        return candidate if candidate != root and root in candidate.parents else None

    def failure(message, status=400):
        return jsonify(ok=False, message=str(message)), status

    @app.get("/")
    def index():
        return render_template("index.html", calendar_token=os.getenv("CALENDAR_TOKEN", ""))

    @app.get("/favicon.ico")
    def favicon():
        return app.send_static_file("favicon.svg")

    @app.get("/calendar.ics")
    def calendar():
        token = os.getenv("CALENDAR_TOKEN", "").strip()
        if token and request.args.get("token", "") != token:
            return failure("Unauthorized", 403)
        return Response(calendar_text(load()), mimetype="text/calendar",
                        headers={"Content-Disposition": 'inline; filename="radio-recorder.ics"',
                                 "Cache-Control": "no-store"})

    @app.get("/api/calendar.ics")
    def calendar_download():
        return Response(calendar_text(load(), recurring=False), mimetype="text/calendar",
                        headers={"Content-Disposition": 'attachment; filename="radio-recorder.ics"'})

    @app.get("/api/data")
    def data():
        with lock:
            status = {name: {key: value for key, value in item.items() if key != "station"}
                      for name, item in state.items()}
            return jsonify(stations=load(), status=status)

    def json_file(name, empty_key):
        try:
            path = config_root / name
            return jsonify(json.loads(path.read_text(encoding="utf-8")) if path.exists() else {empty_key: { } if empty_key == "stations" else []})
        except Exception as exc:
            return jsonify(**{empty_key: {} if empty_key == "stations" else [], "error": str(exc)})

    @app.get("/api/health")
    def health():
        return json_file("stream-health.json", "stations")

    @app.get("/api/executions")
    def executions():
        return json_file("executions.json", "executions")

    @app.get("/api/overview")
    def overview():
        files = [path for path in root.rglob("*") if path.is_file()]
        total_bytes = sum(path.stat().st_size for path in files)
        with lock:
            recording = sum(item.get("status") == "recording" for item in state.values())
        try:
            disk = shutil.disk_usage(root)
        except OSError:
            disk = None
        stations = load(); station_usage = []; maximum = 1; raw = []
        directories = [path for path in root.iterdir() if path.is_dir()] if root.exists() else []
        for station in stations:
            safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in str(station.get("name", ""))).strip("._") or "station"
            directory = next((path for path in directories if path.name.casefold() == safe_name.casefold()), root / safe_name)
            size = sum(path.stat().st_size for path in directory.rglob("*") if path.is_file()) if directory.exists() else 0
            try: limit = int(float(station.get("max_storage_gb", 0) or 0) * 1024**3)
            except (TypeError, ValueError): limit = 0
            raw.append((station.get("name", ""), size, limit)); maximum = max(maximum, size)
        for name, size, limit in raw:
            station_usage.append({"station": name, "bytes": size, "size": human(size), "limit_bytes": limit,
                                  "limit": human(limit) if limit else "", "relative_percent": round(size / maximum * 100, 1)})
        return jsonify(stations=len(stations), recording=recording, files=len(files), size=human(total_bytes),
                       free=human(disk.free) if disk else "—", disk_total_bytes=disk.total if disk else 0,
                       disk_used_bytes=disk.used if disk else 0, disk_total=human(disk.total) if disk else "—",
                       disk_used=human(disk.used) if disk else "—", station_usage=station_usage)

    @app.get("/api/library")
    def library():
        output = []
        for path in root.rglob("*"):
            if not path.is_file(): continue
            relative = path.relative_to(root); parts = relative.parts; stat = path.stat()
            output.append({"station": parts[0] if parts else "", "date": parts[1] if len(parts) > 2 else "",
                           "name": path.name, "path": str(relative), "size": human(stat.st_size), "mtime": stat.st_mtime})
        return jsonify(files=sorted(output, key=lambda item: item["mtime"], reverse=True)[:1000])

    @app.get("/api/stats")
    def stats():
        output = []
        for directory in root.iterdir() if root.exists() else []:
            if not directory.is_dir(): continue
            files = [path for path in directory.rglob("*") if path.is_file()]
            size = sum(path.stat().st_size for path in files)
            output.append({"station": directory.name, "files": len(files), "size": human(size), "bytes": size})
        return jsonify(output)

    @app.get("/api/backup")
    def backup():
        return Response(json.dumps({"stations": load()}, ensure_ascii=False, indent=2), mimetype="application/json",
                        headers={"Content-Disposition": 'attachment; filename="stations-backup.json"'})

    @app.get("/media")
    def media():
        path = media_path(request.args.get("path", ""))
        if path is None or not path.is_file(): abort(404)
        return send_file(path, as_attachment="download" in request.args, download_name=path.name, conditional=True)

    @app.post("/api/start")
    @app.post("/api/stop")
    def manual_action():
        name = request.args.get("name", "")
        with lock:
            if name in state: state[name]["manual"] = request.path.endswith("start")
        return jsonify(ok=True)

    @app.post("/api/save")
    def save_stations():
        try:
            stations = (request.get_json(silent=True) or {}).get("stations")
            if not isinstance(stations, list): raise ValueError("Brak poprawnej listy 'stations' w żądaniu.")
            save(stations); ensure(); reread = load()
            if len(reread) != len(stations): raise OSError("Po zapisie liczba stacji w stations.json jest niezgodna.")
            return jsonify(ok=True, message="Zapisano stations.json", stations=len(reread))
        except PermissionError as exc: return failure(f"Brak uprawnień do /config/stations.json: {exc}", 500)
        except OSError as exc: return failure(f"Błąd zapisu pliku stations.json: {exc}", 500)
        except Exception as exc: return failure(exc)

    @app.post("/api/import-backup")
    def import_backup():
        try:
            stations = (request.get_json(silent=True) or {}).get("stations")
            if not isinstance(stations, list): raise ValueError("Backup nie zawiera listy 'stations'.")
            mode = request.args.get("mode", "merge").lower()
            if mode not in {"merge", "replace"}: raise ValueError("Nieznany tryb importu.")
            config = config_root / "stations.json"; backup_name = ""
            if config.exists():
                backup_path = config.with_name(f"stations.before-import-{dt.datetime.now():%Y%m%d-%H%M%S}.json")
                shutil.copy2(config, backup_path); backup_name = backup_path.name
            stats = {"stations_added": 0, "schedules_added": 0, "duplicates_skipped": 0, "conflicts_skipped": 0}
            result = stations
            if mode == "merge": result, stats = merge_station_configs(load(), stations)
            save(result); ensure(); reread = load()
            if len(reread) != len(result): raise OSError("Weryfikacja importu nie powiodła się.")
            return jsonify(ok=True, mode=mode, stations=len(reread), backup=backup_name, **stats)
        except PermissionError as exc: return failure(f"Brak uprawnień do /config: {exc}", 500)
        except Exception as exc: return failure(exc)

    @app.post("/api/test")
    def test():
        try: return jsonify(test_stream((request.get_json(silent=True) or {}).get("url", "")))
        except Exception as exc: return failure(exc)

    @app.post("/api/delete")
    def delete():
        path = media_path(request.args.get("path", ""))
        if path is None or not path.is_file(): return failure("Nie znaleziono pliku.", 404)
        path.unlink(); return jsonify(ok=True)

    return app


def serve(port, load, save, state, lock, ensure, test, root):
    app = create_app(load, save, state, lock, ensure, test, root)
    from waitress import serve as serve_wsgi
    serve_wsgi(app, host="0.0.0.0", port=port, threads=8)
