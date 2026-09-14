import copy


def _hhmm_minutes(value):
    try:
        h,m=map(int,str(value).split(":",1))
        return h*60+m
    except Exception:
        return None

def _slot_interval(slot):
    start=_hhmm_minutes(slot.get("start"))
    end=_hhmm_minutes(slot.get("end"))
    if start is None or end is None:
        return None
    if end<=start:
        end+=24*60
    return start,end

def _slots_overlap(a,b):
    ia=_slot_interval(a); ib=_slot_interval(b)
    if ia is None or ib is None:
        return False
    a0,a1=ia; b0,b1=ib
    candidates=[(b0,b1),(b0+1440,b1+1440),(b0-1440,b1-1440)]
    return any(max(a0,x0)<min(a1,x1) for x0,x1 in candidates)

def merge_station_configs(existing,incoming):
    """Merge import into current config without deleting current data.

    Existing station settings win. For matching stations, only non-conflicting
    schedule entries are appended. Exact duplicates and nominal-time conflicts
    are skipped. New stations are appended whole.
    """
    import copy
    result=copy.deepcopy(existing if isinstance(existing,list) else [])
    stats={"stations_added":0,"schedules_added":0,"duplicates_skipped":0,"conflicts_skipped":0}
    by_name={}
    for st in result:
        name=str(st.get("name","")).strip().casefold()
        if name and name not in by_name:
            by_name[name]=st

    for src in incoming if isinstance(incoming,list) else []:
        if not isinstance(src,dict):
            continue
        name=str(src.get("name","")).strip()
        if not name:
            continue
        key=name.casefold()
        dst=by_name.get(key)
        if dst is None:
            new_station=copy.deepcopy(src)
            result.append(new_station)
            by_name[key]=new_station
            stats["stations_added"]+=1
            sched=new_station.get("schedule") or {}
            if isinstance(sched,dict):
                stats["schedules_added"]+=sum(len(v) for v in sched.values() if isinstance(v,list))
            continue

        dst_sched=dst.setdefault("schedule",{})
        if not isinstance(dst_sched,dict):
            dst_sched={}
            dst["schedule"]=dst_sched
        src_sched=src.get("schedule") or {}
        if not isinstance(src_sched,dict):
            continue
        for day,slots in src_sched.items():
            if not isinstance(slots,list):
                continue
            current=dst_sched.setdefault(day,[])
            if not isinstance(current,list):
                current=[]
                dst_sched[day]=current
            for slot in slots:
                if not isinstance(slot,dict):
                    continue
                sig=(str(slot.get("start","")),str(slot.get("end","")),str(slot.get("title","")))
                duplicate=any((str(x.get("start","")),str(x.get("end","")),str(x.get("title","")))==sig for x in current if isinstance(x,dict))
                if duplicate:
                    stats["duplicates_skipped"]+=1
                    continue
                if any(_slots_overlap(x,slot) for x in current if isinstance(x,dict)):
                    stats["conflicts_skipped"]+=1
                    continue
                current.append(copy.deepcopy(slot))
                stats["schedules_added"]+=1
            current.sort(key=lambda x:(str(x.get("start","")),str(x.get("end","")),str(x.get("title",""))))
    return result,stats

def human(n):
    n=float(n)
    for u in ["B","KB","MB","GB","TB"]:
        if n<1024:
            return f"{n:.1f} {u}"
        n/=1024
    return f"{n:.1f} PB"
