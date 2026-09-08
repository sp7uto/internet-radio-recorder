import os, json, signal, subprocess, threading, time, shutil, urllib.request
from pathlib import Path
from datetime import datetime, timedelta

CONFIG=os.getenv("CONFIG_FILE","/config/stations.json")
OUT=Path(os.getenv("RECORDINGS_DIR","/recordings"))
RETRY=int(os.getenv("RETRY_DELAY","15"))
PORT=int(os.getenv("WEB_PORT","8080"))
RCHECK=int(os.getenv("RETENTION_CHECK_MINUTES","30"))*60
HEALTHCHECK_SECONDS=max(30,int(os.getenv("HEALTHCHECK_SECONDS","60")))
NTFY_URL=os.getenv("NTFY_URL","").strip()
WEBHOOK_URL=os.getenv("WEBHOOK_URL","").strip()
HEALTHLOG=Path("/config/stream-health.json")

def notify(title,message):
    payload=(title+"\n"+message).encode("utf-8")
    if NTFY_URL:
        try:
            req=urllib.request.Request(NTFY_URL,data=message.encode("utf-8"),method="POST")
            req.add_header("Title",title)
            urllib.request.urlopen(req,timeout=8).read()
        except Exception:
            pass
    if WEBHOOK_URL:
        try:
            body=json.dumps({"title":title,"message":message}).encode("utf-8")
            req=urllib.request.Request(WEBHOOK_URL,data=body,method="POST")
            req.add_header("Content-Type","application/json")
            urllib.request.urlopen(req,timeout=8).read()
        except Exception:
            pass

def load_health():
    try:
        with open(HEALTHLOG,encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"stations":{}}

def save_health(data):
    tmp=str(HEALTHLOG)+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    os.replace(tmp,HEALTHLOG)

EXECLOG=Path("/config/executions.json")

def load_exec():
    try:
        with open(EXECLOG,encoding="utf-8") as f:
            return json.load(f).get("executions",[])
    except Exception:
        return []

def save_exec(items):
    tmp=str(EXECLOG)+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump({"executions":items[-2000:]},f,ensure_ascii=False,indent=2)
    os.replace(tmp,EXECLOG)

def add_exec(item):
    try:
        items=load_exec()
        items.append(item)
        save_exec(items)
    except Exception:
        pass

DAYS=["mon","tue","wed","thu","fri","sat","sun"]

running=True
procs={}
workers={}
state={}
lock=threading.RLock()

def safe(s):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in str(s)).strip("._") or "station"

def load():
    try:
        with open(CONFIG,encoding="utf-8") as f:
            return json.load(f).get("stations",[])
    except Exception:
        return []

def save(stations):
    if not isinstance(stations,list):
        raise ValueError("Pole 'stations' musi być listą.")
    names=[]
    for i,st in enumerate(stations):
        if not isinstance(st,dict):
            raise ValueError(f"Stacja #{i+1} ma nieprawidłowy format.")
        name=str(st.get("name","")).strip()
        url=str(st.get("url","")).strip()
        if not name:
            raise ValueError(f"Stacja #{i+1}: brak nazwy.")
        if not url:
            raise ValueError(f"{name}: brak URL strumienia.")
        names.append(name)
    if len(names)!=len(set(names)):
        raise ValueError("Nazwy stacji muszą być unikalne.")

    cfg=Path(CONFIG)
    cfg.parent.mkdir(parents=True,exist_ok=True)

    # backup poprzedniej wersji
    if cfg.exists():
        bak=cfg.with_suffix(cfg.suffix+".bak")
        shutil.copy2(cfg,bak)

    payload={"stations":stations}
    tmp=str(cfg)+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp,cfg)

    # verify that the written file is valid and readable
    with open(cfg,encoding="utf-8") as f:
        check=json.load(f)
    if not isinstance(check,dict) or not isinstance(check.get("stations"),list):
        raise IOError("Weryfikacja zapisanego stations.json nie powiodła się.")
    return True

def normslot(x):
    if isinstance(x,list):
        return {"start":x[0],"end":x[1],"title":"","pre":0,"post":0}
    return {
        "start":x.get("start","00:00"),
        "end":x.get("end","23:59"),
        "title":x.get("title",""),
        "pre":int(x.get("pre",0) or 0),
        "post":int(x.get("post",0) or 0)
    }

def mm(v):
    h,m=map(int,v.split(":"))
    return h*60+m

def _slot_candidates(st, dt):
    """Return schedule slots around *dt* with real datetime boundaries.

    We inspect yesterday and today so midnight-spanning programs and their
    pre/post margins are handled without special-case minute arithmetic.
    """
    sch=st.get("schedule") or {}
    candidates=[]
    for day_offset in (-1,0):
        day_dt=dt+timedelta(days=day_offset)
        day_key=DAYS[day_dt.weekday()]
        for index,raw in enumerate(sch.get(day_key,[])):
            x=normslot(raw)
            sh,sm=map(int,x["start"].split(":"))
            eh,em=map(int,x["end"].split(":"))
            nominal_start=day_dt.replace(hour=sh,minute=sm,second=0,microsecond=0)
            nominal_end=day_dt.replace(hour=eh,minute=em,second=0,microsecond=0)
            if nominal_end<=nominal_start:
                nominal_end+=timedelta(days=1)
            padded_start=nominal_start-timedelta(minutes=x["pre"])
            padded_end=nominal_end+timedelta(minutes=x["post"])
            identity=f"{day_key}:{index}:{nominal_start.isoformat()}:{x['start']}-{x['end']}"
            slot=dict(x)
            slot["_identity"]=identity
            candidates.append((slot,nominal_start,nominal_end,padded_start,padded_end))
    return candidates

def active(st,dt):
    if not st.get("enabled",True):
        return False,"wyłączona","",None

    candidates=_slot_candidates(st,dt)

    # v2.1.12: nominal program time always beats another slot's pre/post
    # margin.  This makes adjacent programs switch files exactly at their
    # shared boundary instead of being swallowed by overlapping padding.
    nominal=[c for c in candidates if c[1] <= dt < c[2]]
    if nominal:
        x,_,_,_,_=max(nominal,key=lambda c:c[1])
        return True,f'{x["start"]}-{x["end"]}',x["title"],x

    padded=[c for c in candidates if c[3] <= dt < c[4]]
    if padded:
        # Before a program prefer the nearest upcoming start; after it prefer
        # the most recently ended program.  Either way the result is stable.
        upcoming=[c for c in padded if dt < c[1]]
        if upcoming:
            x,_,_,_,_=min(upcoming,key=lambda c:c[1])
        else:
            x,_,_,_,_=max(padded,key=lambda c:c[2])
        return True,f'{x["start"]}-{x["end"]}',x["title"],x

    return False,"poza harmonogramem","",None

def next_schedule(st,now_dt):
    sch=st.get("schedule") or {}
    for add_days in range(8):
        base_dt=now_dt+timedelta(days=add_days)
        key=DAYS[base_dt.weekday()]
        for raw in sch.get(key,[]):
            x=normslot(raw)
            h,m=map(int,x["start"].split(":"))
            candidate=base_dt.replace(hour=h,minute=m,second=0,microsecond=0)-timedelta(minutes=x["pre"])
            if candidate>now_dt:
                return {"when":candidate.isoformat(),"title":x["title"]}
    return None

def ffprobe_info(url):
    try:
        p=subprocess.run(
            ["ffprobe","-v","error","-show_entries","stream=codec_name,bit_rate:format=format_name",
             "-of","json","-rw_timeout","10000000",url],
            capture_output=True,text=True,timeout=15
        )
        if p.returncode!=0:
            return {"ok":False,"message":p.stderr.strip() or "ffprobe error"}
        d=json.loads(p.stdout or "{}")
        streams=d.get("streams") or []
        if not streams:
            return {"ok":False,"message":"Brak strumienia audio."}
        s=streams[0]
        codec=(s.get("codec_name") or "").lower()
        fmt=((d.get("format") or {}).get("format_name") or "").lower()
        if codec=="mp3":
            ext="mp3"
        elif codec in ("aac","aac_latm"):
            ext="aac"
        else:
            ext="aac"
        tags=(d.get("format") or {}).get("tags") or {}
        now_playing=tags.get("StreamTitle") or tags.get("streamtitle") or tags.get("title") or ""
        return {"ok":True,"codec":codec or "unknown","format":fmt or "unknown","bit_rate":s.get("bit_rate"),"ext":ext,"now_playing":now_playing}
    except Exception as e:
        return {"ok":False,"message":str(e)}

def build_cmd(st,out,title,slot):
    ext=st.get("detected_ext") or st.get("codec","aac")
    if ext not in ("aac","mp3","m4a"):
        ext="aac"
    mux={"aac":"adts","mp3":"mp3","m4a":"ipod"}[ext]
    label="_"+safe(title) if title else ""
    one=bool(st.get("one_file_per_program",False)) and slot is not None

    base=["ffmpeg","-hide_banner","-nostdin","-loglevel","warning",
          "-rw_timeout","15000000","-reconnect","1","-reconnect_streamed","1",
          "-reconnect_at_eof","1","-reconnect_delay_max","10",
          "-user_agent","Mozilla/5.0 Internet-Radio-Recorder/2.1.12",
          "-i",st["url"],"-map","0:a:0","-vn","-c:a","copy"]

    if one:
        stamp=datetime.now().strftime("%Y-%m-%d_%H-%M")
        path=str(out/datetime.now().strftime("%Y-%m-%d")/(safe(st["name"])+"_"+stamp+label+"."+ext))
        return base+["-f",mux,path]

    pattern=str(out/"%Y-%m-%d"/(safe(st["name"])+"_%H-%M-%S"+label+"."+ext))
    return base+[
        "-f","segment",
        "-segment_time",str(int(st.get("segment_minutes",60))*60),
        "-segment_atclocktime","1",
        "-reset_timestamps","1",
        "-strftime","1",
        "-segment_format",mux,
        pattern
    ]

def current_recording_info(name):
    try:
        root=OUT/safe(name)
        files=[p for p in root.rglob("*") if p.is_file()]
        if not files:
            return {"file":None,"size":0}
        p=max(files,key=lambda x:x.stat().st_mtime)
        return {"file":str(p.relative_to(OUT)),"size":p.stat().st_size}
    except Exception:
        return {"file":None,"size":0}

def station_usage_bytes(st):
    root=OUT/safe(st["name"])
    if not root.exists():
        return 0
    total=0
    for p in root.rglob("*"):
        if p.is_file():
            try: total+=p.stat().st_size
            except: pass
    return total

def enforce_size_limit(st):
    try:
        limit_gb=float(st.get("max_storage_gb",0) or 0)
    except:
        limit_gb=0
    if limit_gb<=0:
        return
    root=OUT/safe(st["name"])
    if not root.exists():
        return
    limit=int(limit_gb*1024*1024*1024)
    files=[p for p in root.rglob("*") if p.is_file()]
    files.sort(key=lambda p:p.stat().st_mtime)
    total=sum(p.stat().st_size for p in files)
    for p in files:
        if total<=limit:
            break
        try:
            sz=p.stat().st_size
            p.unlink()
            total-=sz
        except:
            pass


def stop_process(name, reason="schedule_end", grace=8):
    p=procs.get(name)
    if not p:
        return
    try:
        if p.poll() is None:
            p.terminate()
            deadline=time.time()+grace
            while p.poll() is None and time.time()<deadline:
                time.sleep(0.2)
            if p.poll() is None:
                p.kill()
                try:
                    p.wait(timeout=3)
                except Exception:
                    pass
        with lock:
            if name in state:
                state[name]["stop_reason"]=reason
                state[name]["stopped_at"]=datetime.now().astimezone().isoformat()
    except Exception as e:
        with lock:
            if name in state:
                state[name]["last_error"]=f"stop_process: {e}"
                state[name]["last_error_at"]=datetime.now().astimezone().isoformat()

def stderr_reader(name, p):
    try:
        for line in p.stderr:
            if not line.strip():
                continue
            msg=line.strip()
            with lock:
                if name in state:
                    state[name]["error"]=msg
                    state[name]["last_error"]=msg
                    state[name]["last_error_at"]=datetime.now().astimezone().isoformat()
    except Exception as e:
        with lock:
            if name in state:
                state[name]["last_error"]=f"stderr_reader: {e}"
                state[name]["last_error_at"]=datetime.now().astimezone().isoformat()

def worker(name):
    while running:
        st=next((x for x in load() if x.get("name")==name),None)
        if not st:
            stop_process(name,"station_removed")
            return

        out=OUT/safe(name)
        out.mkdir(parents=True,exist_ok=True)

        with lock:
            state.setdefault(name,{"manual":False,"reconnects":0,"last_error":"","last_error_at":None})

        now=datetime.now().astimezone()
        ok,label,title,slot=active(st,now)

        with lock:
            manual=state[name].get("manual",False)
            state[name].update(
                schedule=label,
                title=title,
                scheduled=ok,
                next=next_schedule(st,now)
            )

        should_run=st.get("enabled",True) and (manual or ok)
        active_slot_id=(slot or {}).get("_identity") if slot else None

        # Jeśli proces już działa, NIE blokujemy się na stderr.
        # Co sekundę ponownie sprawdzamy harmonogram.
        p=procs.get(name)
        if p is not None:
            if p.poll() is not None:
                procs.pop(name,None)
                time.sleep(0.2)
                continue

            # Manual REC ma działać do ręcznego STOP.
            # Nagranie harmonogramowe kończymy natychmiast po wyjściu z okna.
            if not st.get("enabled",True):
                stop_process(name,"station_disabled")
            elif not manual:
                ok_now, label_now, title_now, slot_now=active(st,datetime.now().astimezone())
                with lock:
                    if name in state:
                        state[name].update(
                            schedule=label_now,
                            title=title_now,
                            scheduled=ok_now
                        )
                if not ok_now:
                    stop_process(name,"schedule_end")
                elif bool(st.get("one_file_per_program",False)):
                    slot_id_now=(slot_now or {}).get("_identity") if slot_now else None
                    running_slot_id=state.get(name,{}).get("recording_slot_id")
                    if running_slot_id and slot_id_now and slot_id_now!=running_slot_id:
                        stop_process(name,"program_change")
            time.sleep(1)
            continue

        if not should_run:
            with lock:
                state[name].update(
                    status="disabled" if not st.get("enabled",True) else "waiting",
                    started=None
                )
            time.sleep(2)
            continue

        (out/datetime.now().strftime("%Y-%m-%d")).mkdir(parents=True,exist_ok=True)

        try:
            with lock:
                state[name].update(status="connecting",error="",stop_reason=None,stopped_at=None)

            started_at=datetime.now().astimezone()
            p=subprocess.Popen(
                build_cmd(st,out,title,slot),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            procs[name]=p

            with lock:
                state[name].update(
                    status="recording",
                    started=started_at.isoformat(),
                    execution_started=started_at.isoformat(),
                    recording_slot_id=active_slot_id
                )

            threading.Thread(target=stderr_reader,args=(name,p),daemon=True).start()

            # Poll zamiast blokującego czytania stderr.
            # Dzięki temu harmonogram może przerwać proces o zadanej porze.
            while running and p.poll() is None:
                st_now=next((x for x in load() if x.get("name")==name),None)
                if not st_now:
                    stop_process(name,"station_removed")
                    break

                with lock:
                    manual_now=state.get(name,{}).get("manual",False)

                if not st_now.get("enabled",True):
                    stop_process(name,"station_disabled")
                    break

                if not manual_now:
                    ok_now,label_now,title_now,slot_now=active(st_now,datetime.now().astimezone())
                    with lock:
                        if name in state:
                            state[name].update(
                                schedule=label_now,
                                title=title_now,
                                scheduled=ok_now,
                                next=next_schedule(st_now,datetime.now().astimezone())
                            )
                    if not ok_now:
                        stop_process(name,"schedule_end")
                        break
                    if bool(st_now.get("one_file_per_program",False)):
                        slot_id_now=(slot_now or {}).get("_identity") if slot_now else None
                        if active_slot_id and slot_id_now and slot_id_now!=active_slot_id:
                            stop_process(name,"program_change")
                            break

                time.sleep(1)

            try:
                p.wait(timeout=3)
            except Exception:
                pass

        except Exception as e:
            with lock:
                state[name].update(
                    status="error",
                    error=str(e),
                    last_error=str(e),
                    last_error_at=datetime.now().astimezone().isoformat()
                )
            notify("Radio Recorder: błąd nagrywania",f"{name}: {e}")

        finally:
            procs.pop(name,None)
            try:
                with lock:
                    stcopy=dict(state.get(name,{}))
                info=current_recording_info(name)
                ended=datetime.now().astimezone()

                exec_status="ok"
                if stcopy.get("last_error"):
                    exec_status="warning"
                if stcopy.get("status")=="error":
                    exec_status="error"

                add_exec({
                    "station":name,
                    "title":title or "",
                    "started":stcopy.get("execution_started") or stcopy.get("started"),
                    "ended":ended.isoformat(),
                    "status":exec_status,
                    "file":info.get("file"),
                    "size":info.get("size",0),
                    "last_error":stcopy.get("last_error",""),
                    "stop_reason":stcopy.get("stop_reason","")
                })

                with lock:
                    if name in state:
                        state[name]["status"]="waiting"
                        state[name]["started"]=None
                        state[name]["recording_slot_id"]=None
            except Exception:
                pass

        # Po prawidłowym zakończeniu harmonogramu nie traktujemy tego jako reconnect.
        with lock:
            reason=state.get(name,{}).get("stop_reason")
        if running and reason not in ("schedule_end","station_disabled","station_removed","program_change"):
            with lock:
                if name in state:
                    state[name]["reconnects"]=int(state[name].get("reconnects",0))+1
                    state[name]["status"]="retrying"
            time.sleep(RETRY)
        elif reason=="program_change":
            time.sleep(0.05)
        else:
            time.sleep(1)

def ensure():
    names={x.get("name") for x in load() if x.get("name")}
    for n in names:
        if n not in workers or not workers[n].is_alive():
            t=threading.Thread(target=worker,args=(n,),daemon=True)
            workers[n]=t
            t.start()
    for n in list(workers):
        if n not in names:
            if n in procs:
                try: procs[n].terminate()
                except: pass
            workers.pop(n,None)
            with lock:
                state.pop(n,None)

def retention_loop():
    while running:
        for st in load():
            try:
                days=int(st.get("retention_days",0) or 0)
            except:
                days=0
            root=OUT/safe(st.get("name",""))
            if days>0 and root.exists():
                cutoff=(datetime.now()-timedelta(days=days)).date()
                for d in root.iterdir():
                    if d.is_dir():
                        try:
                            dd=datetime.strptime(d.name,"%Y-%m-%d").date()
                        except:
                            continue
                        if dd<cutoff:
                            shutil.rmtree(d,ignore_errors=True)
            enforce_size_limit(st)

        for _ in range(max(1,RCHECK)):
            if not running:
                return
            time.sleep(1)

def monitor_loop():
    while running:
        with lock:
            names=list(state.keys())
        for n in names:
            info=current_recording_info(n)
            with lock:
                if n in state:
                    state[n]["current_file"]=info["file"]
                    state[n]["current_size"]=info["size"]
        time.sleep(2)

def test(url):
    return ffprobe_info(url)


def health_loop():
    previous={}
    while running:
        data=load_health()
        stations_data=data.setdefault("stations",{})
        now=datetime.now().astimezone().isoformat()
        for st in load():
            name=st.get("name","")
            info=ffprobe_info(st.get("url",""))
            rec=stations_data.setdefault(name,{"checks":0,"ok":0,"fail":0,"history":[]})
            rec["checks"]=int(rec.get("checks",0))+1
            if info.get("ok"):
                rec["ok"]=int(rec.get("ok",0))+1
                status="online"
            else:
                rec["fail"]=int(rec.get("fail",0))+1
                status="offline"
            rec["last_status"]=status
            rec["last_check"]=now
            rec["codec"]=info.get("codec")
            rec["format"]=info.get("format")
            rec["bit_rate"]=info.get("bit_rate")
            rec["now_playing"]=info.get("now_playing","")
            rec["last_error"]="" if info.get("ok") else info.get("message","")
            hist=rec.setdefault("history",[])
            hist.append({"ts":now,"status":status})
            if len(hist)>1440:
                del hist[:-1440]
            prev=previous.get(name)
            if prev=="online" and status=="offline":
                notify("Radio Recorder: stream OFFLINE",f"{name}: {rec['last_error']}")
            elif prev=="offline" and status=="online":
                notify("Radio Recorder: stream ONLINE",f"{name}: połączenie przywrócone")
            previous[name]=status
            with lock:
                state.setdefault(name,{"manual":False})
                state[name]["stream_health"]=rec
        save_health(data)
        for _ in range(HEALTHCHECK_SECONDS):
            if not running:return
            time.sleep(1)


def stop(*_):
    global running
    running=False
    for p in list(procs.values()):
        try: p.terminate()
        except: pass

signal.signal(signal.SIGTERM,stop)
signal.signal(signal.SIGINT,stop)

if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    ensure()
    threading.Thread(target=retention_loop,daemon=True).start()
    threading.Thread(target=monitor_loop,daemon=True).start()
    threading.Thread(target=health_loop,daemon=True).start()

    def watcher():
        while running:
            ensure()
            time.sleep(5)

    threading.Thread(target=watcher,daemon=True).start()

    from web import serve
    serve(PORT,load,save,state,lock,ensure,test,OUT)
