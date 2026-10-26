#!/usr/bin/env python3
"""IRR updater guard: fail closed if a safe gap cannot be proved."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

CONTAINER = os.environ.get("IRR_CONTAINER", "Internet-Radio-Recorder")
MINUTES = int(os.environ.get("IRR_MIN_IDLE_MINUTES", "20"))
TZ = os.environ.get("IRR_TZ", "Europe/Warsaw")

FETCH_JSON = """
import json, os, urllib.request
port=int(os.environ.get('WEB_PORT', '8080'))
with urllib.request.urlopen('http://127.0.0.1:%d/api/data' % port, timeout=7) as res:
    data=json.load(res)
print(json.dumps(data, ensure_ascii=False))
"""

# Execute inside the recorder container, avoiding host-specific docker top/ps options.
# Treat unreadable /proc as an error; the updater must fail closed.
FFMPEG_SCAN = """
import os
from pathlib import Path

root = Path('/proc')
if not root.is_dir():
    raise SystemExit('PROC_UNAVAILABLE')
for entry in root.iterdir():
    if not entry.name.isdigit():
        continue
    try:
        data = (entry / 'cmdline').read_bytes()
    except (FileNotFoundError, ProcessLookupError):
        continue  # Process exited during the scan.
    except PermissionError:
        raise SystemExit('PROC_PERMISSION_DENIED')
    if not data:
        continue
    command = os.path.basename(data.split(bytes([0]), 1)[0].decode('utf-8', 'replace'))
    if command == 'ffmpeg':
        print('FFMPEG_ACTIVE')
        raise SystemExit(0)
print('FFMPEG_IDLE')
"""

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def reject(reason):
    return False, reason


def check(data, now):
    if not isinstance(data, dict) or not isinstance(data.get("stations"), list):
        return reject("Brak listy stacji")
    stations, states = data["stations"], data.get("status")
    if not stations or not isinstance(states, dict):
        return reject("Brak informacji o stanie")
    if now.tzinfo is None:
        return reject("Brak strefy czasu")
    local_now = now.astimezone(ZoneInfo(TZ))
    for st in stations:
        if not isinstance(st, dict) or not isinstance(st.get("name"), str) or not st["name"]:
            return reject("Nieprawidlowy rekord stacji")
        if not st.get("enabled", True):
            continue
        name = st["name"]
        state = states.get(name)
        if not isinstance(state, dict):
            return reject("Brak statusu stacji " + name)
        if state.get("manual") or state.get("scheduled"):
            return reject("REC lub harmonogram aktywny: " + name)
        if state.get("status") != "waiting":
            return reject("Stacja nie czeka: " + name)
        next_slot = state.get("next")
        if next_slot is not None:
            try:
                dt = datetime.fromisoformat(str(next_slot["when"]))
                if dt.tzinfo is None:
                    raise ValueError("No timezone")
            except (ValueError, KeyError, TypeError, AttributeError):
                return reject("Niezrozumialy termin nagrania: " + name)
            if dt - now < timedelta(minutes=MINUTES):
                return reject("Zbyt bliskie nagranie: " + name)

        schedule = st.get("schedule") or {}
        if not isinstance(schedule, dict):
            return reject("Niezrozumialy harmonogram: " + name)
        has_slots = False
        for key, slots in schedule.items():
            if key not in DAYS or not isinstance(slots, list):
                return reject("Niezrozumialy dzien harmonogramu: " + name)
            if slots:
                has_slots = True
            for raw in slots:
                if not isinstance(raw, dict):
                    return reject("Niezrozumialy wpis harmonogramu: " + name)
                try:
                    hh, mm = [int(x) for x in raw["start"].split(":")]
                    if not (0 <= hh <= 23 and 0 <= mm <= 59):
                        raise ValueError("time")
                    pre = int(raw.get("pre", 0))
                    if pre < 0:
                        raise ValueError("pre")
                except (KeyError, ValueError, TypeError, AttributeError):
                    return reject("Niepoprawna godzina w harmonogramie: " + name)
                for days_ahead in range(-1, 8):
                    day = local_now.date() + timedelta(days=days_ahead)
                    if DAYS[day.weekday()] != key:
                        continue
                    when = datetime(day.year, day.month, day.day, hh, mm, tzinfo=ZoneInfo(TZ)) - timedelta(minutes=pre)
                    if timedelta(0) <= when - local_now < timedelta(minutes=MINUTES):
                        return reject("Bliski start z harmonogramu: " + name)
        if has_slots and next_slot is None:
            return reject("Brak terminu nastepnej audycji mimo harmonogramu: " + name)
    return True, "Bezpieczne okno serwisowe (kontrola orientacyjna)"


def main():
    if MINUTES < 20:
        print("IRR UPDATE DEFERRED: margines musi wynosic >=20 minut")
        return 1
    for command, error in [
        (["docker", "inspect", "-f", "{{.State.Running}}", CONTAINER], "Kontener niedostepny"),
        (["docker", "exec", CONTAINER, "python3", "-c", FFMPEG_SCAN], "Nie mozna sprawdzic FFmpeg"),
        (["docker", "exec", CONTAINER, "python3", "-c", FETCH_JSON], "API /api/data nie odpowiada"),
    ]:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=18)
        if proc.returncode:
            print("IRR UPDATE DEFERRED: " + error)
            return 1
        if command[1] == "inspect" and proc.stdout.strip() != "true":
            print("IRR UPDATE DEFERRED: kontener nie dziala")
            return 1
        if command[1] == "exec" and command[-1] == FFMPEG_SCAN:
            if proc.stdout.strip() != "FFMPEG_IDLE":
                print("IRR UPDATE DEFERRED: trwa proces FFmpeg lub nieznany wynik kontroli")
                return 1
        if command[-1] == FETCH_JSON:
            data = json.loads(proc.stdout)
            allowed, reason = check(data, datetime.now(timezone.utc))
            print(("IRR UPDATE ALLOWED: " if allowed else "IRR UPDATE DEFERRED: ") + reason)
            return 0 if allowed else 1
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        sys.exit("IRR UPDATE DEFERRED: kontrola nie powiodla sie: " + str(exc))
