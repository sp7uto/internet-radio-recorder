import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs,unquote

PAGE = r"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Internet Radio Recorder v2.1.12</title>
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
<style>
:root{
  --bg:#101317; --panel:#1b2027; --line:#303844; --text:#eef2f7;
  --muted:#98a2b3; --green:#4ade80; --blue:#60a5fa; --red:#fb7185;
}
*{box-sizing:border-box}
body{font:15px system-ui;background:var(--bg);color:var(--text);max-width:1180px;margin:auto;padding:20px}
h1{margin-bottom:6px}
.subtitle{color:var(--muted);margin-bottom:18px}
.topstats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:16px}
.stat,.card{background:var(--panel);border:1px solid var(--line);border-radius:12px}
.stat{padding:14px}.stat b{font-size:24px;display:block}.card{padding:20px;margin:15px 0}
.muted{color:var(--muted);font-size:12px}
.status{font-weight:800}.recording{color:var(--green)}.waiting{color:var(--muted)}.error{color:var(--red)}.connecting{color:var(--blue)}
.now{border-left:4px solid var(--green);padding-left:12px;margin:10px 0}
.file{font-family:ui-monospace,monospace;color:#cbd5e1;word-break:break-all}
input,select{background:#11161d;color:#eee;border:1px solid #4b5563;border-radius:6px;padding:7px}
.slot{display:block;margin:5px 0}
button{padding:8px 12px;margin:4px;border:0;border-radius:7px;cursor:pointer}
.danger{background:#5a1d1d;color:white}.primary{font-weight:700}.save-ok{color:#4ade80;font-weight:800}.save-bad{color:#fb7185;font-weight:800}.save-status{margin-left:8px}
.station-tools{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:8px 0 14px}
.station-card{position:relative;transition:border-color .15s ease,box-shadow .15s ease,opacity .15s ease}
.station-card.dragging{opacity:.55}
.station-card.drop-before{box-shadow:0 -4px 0 var(--blue)}
.station-card.drop-after{box-shadow:0 4px 0 var(--blue)}
.station-order{display:flex;align-items:center;gap:4px;margin:-4px 0 8px}
.drag-handle{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:34px;border:1px solid #4b5563;border-radius:7px;background:#11161d;color:#cbd5e1;cursor:grab;user-select:none;font-size:20px;line-height:1}
.drag-handle:active{cursor:grabbing}
.order-btn{min-width:34px;padding:7px 9px;margin:0}
.order-no{color:var(--muted);font-size:12px;margin-left:4px}
.tabs{margin:10px 0 16px}.hide{display:none}audio{width:100%;max-width:520px}
.libtools{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.diag{margin:10px 0;padding:10px;border:1px solid var(--line);border-radius:8px;background:#141a21}
.diag-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.rec-banner{background:linear-gradient(90deg,#47151d,#261419);border:1px solid #7f1d2d;border-radius:10px;padding:11px 13px;margin:10px 0}
.rec-title{color:#fb7185;font-weight:900;letter-spacing:.4px}
.rec-dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;margin-right:8px;box-shadow:0 0 0 0 rgba(239,68,68,.7);animation:pulse 1.5s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(239,68,68,.7)}70%{box-shadow:0 0 0 9px rgba(239,68,68,0)}100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}}
.storage{margin:10px 0}.storage-head{display:flex;justify-content:space-between;gap:12px;font-size:12px;color:var(--muted);margin-bottom:5px}
.storage-bar{height:10px;background:#283241;border-radius:999px;overflow:hidden;border:1px solid #354153}
.storage-fill{height:100%;background:#3b82f6;border-radius:999px;transition:width .4s ease}
.diskbar{grid-column:1/-1;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.diskbar .storage-bar{height:12px}
.calendar-wrap{overflow-x:auto}
.weekcal{display:grid;grid-template-columns:repeat(7,minmax(170px,1fr));gap:8px;min-width:1190px}
.daycol{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;min-height:220px}
.dayhead{font-weight:800;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.event{border-left:4px solid var(--blue);background:#141a21;border-radius:8px;padding:8px;margin:7px 0}
.event.recording{border-left-color:#ef4444;background:#2a1418}
.event-title{font-weight:800}.event-time{font-size:12px;color:var(--muted)}
.upcoming{display:grid;gap:8px}
.upcoming-row{display:grid;grid-template-columns:110px 1fr 140px;gap:10px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}
@media(max-width:800px){.upcoming-row{grid-template-columns:1fr}.weekcal{min-width:900px}}
.today-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.today-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}
.exec-ok{border-left:4px solid #22c55e}.exec-warning{border-left:4px solid #f59e0b}.exec-error{border-left:4px solid #ef4444}
.timeline{position:relative;padding-left:26px}.timeline:before{content:"";position:absolute;left:10px;top:0;bottom:0;width:2px;background:var(--line)}
.tl-item{position:relative;margin:0 0 12px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}
.tl-item:before{content:"";position:absolute;left:-21px;top:16px;width:10px;height:10px;border-radius:50%;background:var(--blue)}
@media(max-width:800px){.today-grid{grid-template-columns:1fr}}
.health-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.health-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px}
.online{color:#22c55e}.offline{color:#ef4444}
.healthbar{height:8px;background:#27313d;border-radius:999px;overflow:hidden;margin-top:6px}
.healthbar>div{height:100%;background:#22c55e}
.nowplaying{margin-top:8px;padding:8px;background:#141a21;border-radius:8px}
@media(max-width:800px){.health-grid{grid-template-columns:1fr}}
@media(max-width:800px){.diag-grid{grid-template-columns:1fr}}
@media(max-width:800px){.topstats{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<h1>Internet Radio Recorder v2.1.12</h1>
<div class="subtitle">Nagrywanie • harmonogram • retencja • biblioteka • statystyki</div>

<div class="topstats">
  <div class="stat"><span class="muted">Stacje</span><b id="stStations">—</b></div>
  <div class="stat"><span class="muted">Nagrywa teraz</span><b id="stRecording">—</b></div>
  <div class="stat"><span class="muted">Pliki</span><b id="stFiles">—</b></div>
  <div class="stat"><span class="muted">Zajęte miejsce</span><b id="stSize">—</b></div>
  <div class="stat"><span class="muted">Wolne na wolumenie</span><b id="stFree">—</b></div>
  <div class="diskbar">
    <div class="storage-head"><span>Zajętość wolumenu Synology</span><span id="diskText">—</span></div>
    <div class="storage-bar"><div class="storage-fill" id="diskFill" style="width:0%"></div></div>
  </div>
</div>

<div class="tabs">
  <button onclick="tab('today')">Dzisiaj</button>
  <button onclick="tab('stations')">Stacje</button>
  <button onclick="tab('calendar')">Kalendarz</button>
  <button onclick="tab('history')">Historia</button>
  <button onclick="tab('health')">Strumienie</button>
  <button onclick="tab('library')">Biblioteka</button>
  <button onclick="tab('stats')">Statystyki</button>
  <button onclick="location=calendarUrl()">Kalendarz ICS</button>
  <button onclick="backup()">Backup</button>
  <button onclick="document.getElementById('mergeFile').click()">Import / scal</button>
  <input id="mergeFile" type="file" accept=".json,application/json" style="display:none" onchange="importBackup(this,'merge')">
  <button onclick="document.getElementById('replaceFile').click()">Przywróć backup</button>
  <input id="replaceFile" type="file" accept=".json,application/json" style="display:none" onchange="importBackup(this,'replace')">
</div>

<div id="today" class="hide">
  <div class="today-grid">
    <div class="today-card"><span class="muted">Teraz</span><div id="todayNow"></div></div>
    <div class="today-card"><span class="muted">Następnie</span><div id="todayNext"></div></div>
    <div class="today-card"><span class="muted">Dzisiaj</span><div id="todayCount"></div></div>
  </div>
  <div class="card"><h2>Dzisiejsza rozpiska</h2><div id="todayTimeline" class="timeline"></div></div>
</div>
<div id="history" class="hide">
  <div class="card"><h2>Historia wykonania zadań</h2><div id="execHistory"></div></div>
</div>
<div id="stations">
  <div class="station-tools">
    <button onclick="add()">+ DODAJ STACJĘ</button>
    <button class="primary" onclick="saveAll()">ZAPISZ ZMIANY</button>
    <span class="muted">Kolejność: przeciągnij ☰ albo użyj ↑ / ↓, następnie zapisz.</span>
    <span id="saveStatus" class="save-status muted"></span>
  </div>
  <div id="cards"></div>
</div>
<div id="calendar" class="hide">
  <div class="card">
    <h2>Kalendarz tygodniowy</h2>
    <div class="calendar-wrap"><div id="weekCalendar" class="weekcal"></div></div>
  </div>
  <div class="card">
    <h2>Najbliższe zadania</h2>
    <div id="upcomingList" class="upcoming"></div>
  </div>
</div>
<div id="health" class="hide">
  <div class="card"><h2>Stan strumieni</h2><div id="healthList"></div></div>
</div>
<div id="library" class="hide"></div>
<div id="stats" class="hide"></div>

<script>
window.CALENDAR_TOKEN="__CALENDAR_TOKEN__";
const days=[["mon","Pon"],["tue","Wt"],["wed","Śr"],["thu","Czw"],["fri","Pt"],["sat","Sob"],["sun","Nd"]];
let D={stations:[],status:{}};

function esc(x){
  return String(x??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
}
function fmtBytes(n){
  n=+n||0;
  for(const u of ["B","KB","MB","GB","TB"]){
    if(n<1024) return n.toFixed(n<10&&u!="B"?1:0)+" "+u;
    n/=1024;
  }
  return n.toFixed(1)+" PB";
}

function durationFrom(iso){
  if(!iso)return "";
  const sec=Math.max(0,Math.floor((Date.now()-new Date(iso).getTime())/1000));
  const h=Math.floor(sec/3600),m=Math.floor((sec%3600)/60),s=sec%60;
  return (h?h+" h ":"")+(m?m+" min ":"")+s+" s";
}
function until(iso){
  if(!iso)return "";
  let sec=Math.floor((new Date(iso).getTime()-Date.now())/1000);
  if(sec<=0)return "za chwilę";
  const d=Math.floor(sec/86400);sec%=86400;
  const h=Math.floor(sec/3600);sec%=3600;
  const m=Math.floor(sec/60);
  return (d?d+" d ":"")+(h?h+" h ":"")+m+" min";
}
function tab(x){
  for(const n of ["today","stations","calendar","history","health","library","stats"])
    document.getElementById(n).classList.toggle("hide",n!==x);
  if(x==="today")   if(x==="calendar")   if(x==="history") loadHistory();
  if(x==="health") loadHealth();
  if(x==="library") lib();
  if(x==="stats") stat();
}
function slotHtml(x={start:"00:00",end:"23:59",title:"",pre:0,post:0}){
  if(Array.isArray(x)) x={start:x[0],end:x[1],title:"",pre:0,post:0};
  return `<span class="slot">
    <input class="a" type="time" value="${esc(x.start)}"> -
    <input class="b" type="time" value="${esc(x.end)}">
    <input class="t" placeholder="Nazwa audycji" value="${esc(x.title||"")}">
    pre <input class="pre" type="number" min="0" value="${+x.pre||0}" style="width:50px">
    post <input class="post" type="number" min="0" value="${+x.post||0}" style="width:50px"> min
    <button onclick="this.parentElement.remove()">x</button>
  </span>`;
}
function render(){
  cards.innerHTML=D.stations.map((s,i)=>{
    const st=D.status[s.name]||{};
    let h=`<div class="card station-card" data-i="${i}" data-detected-ext="${esc(s.detected_ext||s.codec||"aac")}"
        ondragover="dragStationOver(event,${i})" ondragleave="dragStationLeave(event)" ondrop="dropStation(event,${i})">
      <div class="station-order">
        <span class="drag-handle" draggable="true" title="Przeciągnij stację" ondragstart="dragStationStart(event,${i})" ondragend="dragStationEnd(event)">☰</span>
        <button class="order-btn" title="Przenieś wyżej" onclick="moveStation(${i},-1)" ${i===0?"disabled":""}>↑</button>
        <button class="order-btn" title="Przenieś niżej" onclick="moveStation(${i},1)" ${i===D.stations.length-1?"disabled":""}>↓</button>
        <span class="order-no">pozycja ${i+1} z ${D.stations.length}</span>
      </div>
      <h2><input class="name" value="${esc(s.name)}">
      <small class="status status-${i} ${esc(st.status||"waiting")}">${esc(st.status||"—")}</small></h2>`;

    if(st.next && st.status!=="recording"){
      h+=`<div class="muted">Następne: ${esc(st.next.when||"")}${st.next.title?" — "+esc(st.next.title):""} <b class="countdown" data-when="${esc(st.next.when||"")}">(${until(st.next.when)})</b></div>`;
    }
    if(st.status==="recording"){
      h+=`<div class="rec-banner"><div class="rec-title"><span class="rec-dot"></span>TERAZ NAGRYWA</div>
        <div class="file">${esc(st.current_file||"")}</div>
        <div>${fmtBytes(st.current_size||0)}</div>
        ${st.started?`<div class="muted">Od: ${esc(st.started)} • czas: <b class="duration" data-start="${esc(st.started)}">${durationFrom(st.started)}</b></div>`:""}
      </div>`;
    }

    h+=`<input class="url" value="${esc(s.url||"")}" style="width:75%">
      <button onclick="testStream(${i})">Test streamu</button>
      <span class="res"></span>
      <p>
        Segment <input class="seg" type="number" min="1" value="${+s.segment_minutes||60}" style="width:60px"> min;
        retencja <select class="ret">
          <option value="0">nigdy</option>
          ${[7,14,30,60,90,180,365].map(x=>`<option value="${x}" ${+s.retention_days===x?"selected":""}>${x} dni</option>`).join("")}
        </select>
        limit <input class="maxgb" type="number" min="0" step="1" value="${+s.max_storage_gb||0}" style="width:70px"> GB
        <label><input class="one" type="checkbox" ${s.one_file_per_program?"checked":""}> 1 plik / audycję</label>
        <label><input class="en" type="checkbox" ${s.enabled!==false?"checked":""}> aktywna</label>
      </p>
      <div class="storage">
        <div class="storage-head"><span>Zajętość nagrań</span><span class="station-storage-text" data-station="${esc(s.name)}">—</span></div>
        <div class="storage-bar"><div class="storage-fill station-storage-fill" data-station="${esc(s.name)}" style="width:0%"></div></div>
      </div>`;

    for(const [k,label] of days){
      h+=`<div><b>${label}</b>
        <span class="day" data-day="${k}">${(s.schedule?.[k]||[]).map(slotHtml).join("")}</span>
        <button onclick="this.previousElementSibling.insertAdjacentHTML('beforeend',slotHtml())">+ audycja</button>
      </div>`;
    }

    h+=`<div class="diag"><b>Diagnostyka streamu</b>
      <div class="diag-grid">
        <div><span class="muted">Reconnecty</span><br><b>${st.reconnects||0}</b></div>
        <div><span class="muted">Ostatni błąd</span><br>${esc(st.last_error||"brak")}</div>
        <div><span class="muted">Kiedy</span><br>${esc(st.last_error_at||"—")}</div>
        <div><span class="muted">Ostatnie zatrzymanie</span><br>${esc(st.stop_reason||"—")}${st.stopped_at?" • "+esc(st.stopped_at):""}</div>
      </div>
    </div><p>
      <button class="primary" onclick="saveAll()">Zapisz</button>
      <button onclick="action('start','${esc(s.name)}')">REC</button>
      <button onclick="action('stop','${esc(s.name)}')">STOP</button>
      <button class="danger" onclick="removeStation(${i})">Usuń</button>
    </p></div>`;
    return h;
  }).join("");
}

function q(c,sel){return c.querySelector(sel)}
function val(c,sel,def=""){
  const el=q(c,sel);
  return el ? el.value : def;
}
function num(c,sel,def=0){
  const el=q(c,sel);
  return el ? (+el.value||0) : def;
}
function chk(c,sel,def=false){
  const el=q(c,sel);
  return el ? !!el.checked : def;
}

function readCard(c){
  const name=val(c,".name","").trim();
  const url=val(c,".url","").trim();

  const s={
    name,
    url,
    codec:c.dataset.detectedExt||"aac",
    detected_ext:c.dataset.detectedExt||"aac",
    segment_minutes:num(c,".seg",60) || 60,
    retention_days:num(c,".ret",0),
    max_storage_gb:num(c,".maxgb",0),
    one_file_per_program:chk(c,".one",false),
    enabled:chk(c,".en",true),
    schedule:{}
  };

  for(const [k] of days){
    s.schedule[k]=[...c.querySelectorAll(`.day[data-day="${k}"] .slot`)].map(x=>({
      start:val(x,".a","00:00"),
      end:val(x,".b","23:59"),
      title:val(x,".t",""),
      pre:num(x,".pre",0),
      post:num(x,".post",0)
    }));
  }
  return s;
}





function normalizeSlot(x){
  if(Array.isArray(x)) return {start:x[0],end:x[1],title:"",pre:0,post:0};
  return {
    start:x?.start||"00:00",
    end:x?.end||"23:59",
    title:x?.title||"",
    pre:+(x?.pre||0),
    post:+(x?.post||0)
  };
}
function hmToMinutes(hm){
  const [h,m]=String(hm||"00:00").split(":").map(Number);
  return (h||0)*60+(m||0);
}
function minutesToHm(total){
  total=((total%1440)+1440)%1440;
  return String(Math.floor(total/60)).padStart(2,"0")+":"+String(total%60).padStart(2,"0");
}
function weekdayKey(date){
  return ["sun","mon","tue","wed","thu","fri","sat"][date.getDay()];
}
function dayIndex(key){
  return {sun:0,mon:1,tue:2,wed:3,thu:4,fri:5,sat:6}[key];
}
function buildScheduleEvents(){
  const events=[];
  (D.stations||[]).forEach(st=>{
    const schedule=st.schedule||{};
    Object.entries(schedule).forEach(([day,raws])=>{
      if(dayIndex(day)===undefined)return;
      (raws||[]).forEach(raw=>{
        const x=normalizeSlot(raw);
        const schedStart=hmToMinutes(x.start);
        const schedEnd=hmToMinutes(x.end);
        const recStart=schedStart-x.pre;
        let recEnd=schedEnd+x.post;
        let crossesMidnight = schedEnd<=schedStart;
        if(crossesMidnight) recEnd+=1440;
        events.push({
          station:st.name,
          day,
          title:x.title||"(bez nazwy)",
          scheduleStart:x.start,
          scheduleEnd:x.end,
          startMin:recStart,
          endMin:recEnd,
          start:minutesToHm(recStart),
          end:minutesToHm(recEnd),
          pre:x.pre,
          post:x.post,
          crossesMidnight
        });
      });
    });
  });
  return events;
}
function dateForEvent(ev, occurrenceOffsetWeeks=0){
  const now=new Date();
  const delta=(dayIndex(ev.day)-now.getDay()+7)%7;
  const d=new Date(now);
  d.setDate(now.getDate()+delta+occurrenceOffsetWeeks*7);
  const baseStart=hmToMinutes(ev.start);
  // pre może cofnąć start do poprzedniego dnia
  if(ev.startMin<0)d.setDate(d.getDate()-1);
  d.setHours(Math.floor(baseStart/60),baseStart%60,0,0);
  return d;
}
function eventIsToday(ev, now=new Date()){
  // Dzisiejsza rozpiska pokazuje zadania przypisane do dzisiejszego dnia harmonogramu.
  return ev.day===weekdayKey(now);
}
function eventIsRunningNow(ev, now=new Date()){
  // wylicz rzeczywisty przedział daty dla bieżącego tygodnia
  const targetDay=dayIndex(ev.day);
  let delta=targetDay-now.getDay();
  const base=new Date(now);
  base.setHours(0,0,0,0);
  base.setDate(base.getDate()+delta);
  const start=new Date(base);
  start.setMinutes(ev.startMin);
  const end=new Date(base);
  end.setMinutes(ev.endMin);
  // sprawdź też poprzedni tydzień dla zadań przechodzących przez północ
  if(now>=start && now<end)return true;
  const pstart=new Date(start);pstart.setDate(pstart.getDate()-7);
  const pend=new Date(end);pend.setDate(pend.getDate()-7);
  return now>=pstart && now<pend;
}
function renderToday(){
  const now=new Date();
  const todays=buildScheduleEvents()
    .filter(ev=>eventIsToday(ev,now))
    .sort((a,b)=>a.startMin-b.startMin);

  const current=todays.filter(ev=>eventIsRunningNow(ev,now));
  const nowMin=now.getHours()*60+now.getMinutes();
  const next=todays.find(ev=>ev.startMin>nowMin);

  const n=document.getElementById("todayNow");
  const nx=document.getElementById("todayNext");
  const cnt=document.getElementById("todayCount");
  const tl=document.getElementById("todayTimeline");
  if(!n||!nx||!cnt||!tl)return;

  n.innerHTML=current.length
    ? current.map(ev=>`<b>${esc(ev.station)}</b><br>${esc(ev.title)}<br><span class="muted">${esc(ev.start)}–${esc(ev.end)}</span>`).join("<hr>")
    : '<span class="muted">Nic teraz nie jest zaplanowane.</span>';

  nx.innerHTML=next
    ? `<b>${esc(next.station)}</b><br>${esc(next.title)}<br><span class="muted">${esc(next.start)}–${esc(next.end)}</span>`
    : '<span class="muted">Brak kolejnych zadań dzisiaj.</span>';

  cnt.innerHTML=`<b style="font-size:26px">${todays.length}</b><br><span class="muted">zaplanowanych zadań</span>`;

  tl.innerHTML=todays.length
    ? todays.map(ev=>`<div class="tl-item"><b>${esc(ev.start)}–${esc(ev.end)}</b><br>${esc(ev.station)} — ${esc(ev.title)}</div>`).join("")
    : '<div class="muted">Brak zadań na dziś.</div>';
}
function renderCalendar(){
  const week=document.getElementById("weekCalendar");
  const upcoming=document.getElementById("upcomingList");
  if(!week||!upcoming)return;

  const labels={mon:"Poniedziałek",tue:"Wtorek",wed:"Środa",thu:"Czwartek",fri:"Piątek",sat:"Sobota",sun:"Niedziela"};
  const keys=["mon","tue","wed","thu","fri","sat","sun"];
  const all=buildScheduleEvents();

  week.innerHTML=keys.map(k=>{
    const events=all.filter(ev=>ev.day===k).sort((a,b)=>a.startMin-b.startMin);
    return `<div class="daycol"><div class="dayhead">${labels[k]}</div>`+
      (events.length?events.map(ev=>{
        const st=(D.status||{})[ev.station]||{};
        const rec=st.status==="recording" && (!st.title || st.title===ev.title);
        return `<div class="event ${rec?"recording":""}">
          <div class="event-title">${esc(ev.station)} — ${esc(ev.title)}</div>
          <div class="event-time">${esc(ev.start)} – ${esc(ev.end)}</div>
        </div>`;
      }).join(""):`<div class="muted">Brak zadań</div>`)+`</div>`;
  }).join("");

  const now=new Date();
  const rows=[];
  all.forEach(ev=>{
    let when=dateForEvent(ev,0);
    if(when<=now)when=dateForEvent(ev,1);
    rows.push({...ev,when});
  });
  rows.sort((a,b)=>a.when-b.when);
  upcoming.innerHTML=rows.slice(0,20).map(ev=>`<div class="upcoming-row">
    <div><b>${ev.when.toLocaleDateString()}</b><br>${esc(ev.start)}</div>
    <div><b>${esc(ev.station)}</b><br>${esc(ev.title)}</div>
    <div class="countdown" data-when="${ev.when.toISOString()}">${until(ev.when.toISOString())}</div>
  </div>`).join("") || '<div class="muted">Brak zaplanowanych zadań.</div>';
}

async function saveAll(){
  saveStatus.className="save-status muted";
  saveStatus.style.color="";
  saveStatus.textContent="Zapisywanie...";
  try{
    const cards=[...document.querySelectorAll("#cards .card")];
    if(!cards.length){
      throw new Error("Nie znaleziono pól formularza stacji.");
    }
    D.stations=cards.map(readCard);
    const r=await fetch("/api/save",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({stations:D.stations})
    });
    const j=await r.json();
    if(!r.ok || !j.ok){
      saveStatus.className="save-status save-bad";
      saveStatus.textContent="Błąd zapisu: "+(j.message||("HTTP "+r.status));
      return;
    }
    saveStatus.className="save-status save-ok";
    saveStatus.textContent="Zapisano ✓";
    await fullLoad();
    if(typeof renderCalendar==="function") renderCalendar();
    setTimeout(()=>{saveStatus.textContent=""},4000);
  }catch(e){
    saveStatus.className="save-status save-bad";
    saveStatus.textContent="Błąd zapisu: "+e;
  }
}

let draggedStationIndex=null;

function captureStationForms(){
  const cs=[...document.querySelectorAll("#cards .station-card")];
  if(cs.length) D.stations=cs.map(readCard);
}
function markOrderDirty(){
  saveStatus.className="save-status";
  saveStatus.style.color="#f59e0b";
  saveStatus.textContent="Kolejność zmieniona — kliknij ZAPISZ ZMIANY";
}
function moveStation(i,delta){
  captureStationForms();
  const j=i+delta;
  if(i<0||j<0||i>=D.stations.length||j>=D.stations.length)return;
  const [st]=D.stations.splice(i,1);
  D.stations.splice(j,0,st);
  render();
  markOrderDirty();
}
function dragStationStart(ev,i){
  captureStationForms();
  draggedStationIndex=i;
  ev.dataTransfer.effectAllowed="move";
  ev.dataTransfer.setData("text/plain",String(i));
  const card=ev.currentTarget.closest(".station-card");
  if(card) setTimeout(()=>card.classList.add("dragging"),0);
}
function clearDropMarks(){
  document.querySelectorAll("#cards .station-card").forEach(c=>c.classList.remove("drop-before","drop-after"));
}
function dragStationOver(ev,i){
  if(draggedStationIndex===null)return;
  ev.preventDefault();
  ev.dataTransfer.dropEffect="move";
  clearDropMarks();
  const card=ev.currentTarget;
  const r=card.getBoundingClientRect();
  card.classList.add(ev.clientY < r.top+r.height/2 ? "drop-before" : "drop-after");
}
function dragStationLeave(ev){
  const card=ev.currentTarget;
  if(!card.contains(ev.relatedTarget)) card.classList.remove("drop-before","drop-after");
}
function dropStation(ev,targetIndex){
  if(draggedStationIndex===null)return;
  ev.preventDefault();
  const from=draggedStationIndex;
  const card=ev.currentTarget;
  const r=card.getBoundingClientRect();
  const after=ev.clientY >= r.top+r.height/2;
  let insertAt=targetIndex+(after?1:0);
  const [st]=D.stations.splice(from,1);
  if(insertAt>from)insertAt--;
  insertAt=Math.max(0,Math.min(D.stations.length,insertAt));
  D.stations.splice(insertAt,0,st);
  draggedStationIndex=null;
  clearDropMarks();
  render();
  markOrderDirty();
}
function dragStationEnd(){
  draggedStationIndex=null;
  clearDropMarks();
  document.querySelectorAll("#cards .station-card.dragging").forEach(c=>c.classList.remove("dragging"));
}

function add(){
  D.stations.push({name:"Nowa stacja",url:"",codec:"aac",detected_ext:"aac",segment_minutes:60,retention_days:0,max_storage_gb:0,one_file_per_program:false,enabled:false,schedule:{}});
  render();
  window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"});
}
function removeStation(i){
  if(confirm("Usunąć stację? Nagrania pozostaną.")){
    D.stations.splice(i,1);
    render();
  }
}
async function action(a,n){
  await fetch("/api/"+a+"?name="+encodeURIComponent(n),{method:"POST"});
  await statusLoad();
}
async function testStream(i){
  const c=document.querySelector(`.card[data-i="${i}"]`);
  const r=await fetch("/api/test",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:c.querySelector(".url").value})});
  const j=await r.json();
  if(j.ok){
    c.dataset.detectedExt=j.ext||"aac";
    c.querySelector(".res").textContent=` OK: ${j.codec||""} / ${j.format||""} -> .${j.ext||"aac"}`;
  }else{
    c.querySelector(".res").textContent=` Błąd: ${j.message||"nieznany"}`;
  }
}
let LIBFILES=[];
function renderLibrary(){
  const q=(document.getElementById("libSearch")?.value||"").toLowerCase();
  const station=document.getElementById("libStation")?.value||"";
  const range=document.getElementById("libRange")?.value||"all";
  const now=Date.now();
  let rows=LIBFILES.filter(f=>{
    if(station && f.station!==station)return false;
    if(q && !(f.name+" "+f.station+" "+f.date).toLowerCase().includes(q))return false;
    if(range!=="all"){
      const days=+range;
      if((now-(f.mtime*1000)) > days*86400000)return false;
    }
    return true;
  });
  document.getElementById("libList").innerHTML=rows.map(f=>`<div class="card">
    <b>${esc(f.station)}</b> — ${esc(f.date)} — ${esc(f.name)} (${f.size})<br>
    <audio controls preload="none" src="/media?path=${encodeURIComponent(f.path)}"></audio>
    <a href="/media?download=1&path=${encodeURIComponent(f.path)}">Pobierz</a>
    <button onclick="removeFile('${encodeURIComponent(f.path)}')">Usuń</button>
  </div>`).join("") || '<div class="muted">Brak nagrań pasujących do filtrów.</div>';
}
async function lib(){
  const j=await(await fetch("/api/library")).json();
  LIBFILES=j.files||[];
  const stations=[...new Set(LIBFILES.map(x=>x.station))].sort();
  library.innerHTML=`<h2>Biblioteka</h2>
    <div class="libtools">
      <input id="libSearch" placeholder="Szukaj: stacja, audycja, data..." oninput="renderLibrary()">
      <select id="libStation" onchange="renderLibrary()"><option value="">Wszystkie stacje</option>${stations.map(x=>`<option>${esc(x)}</option>`).join("")}</select>
      <select id="libRange" onchange="renderLibrary()"><option value="all">Całe archiwum</option><option value="1">Dzisiaj / 24 h</option><option value="7">7 dni</option><option value="30">30 dni</option><option value="90">90 dni</option></select>
    </div><div id="libList"></div>`;
  renderLibrary();
}
async function removeFile(p){
  if(confirm("Usunąć plik?")){
    await fetch("/api/delete?path="+p,{method:"POST"});
    await lib();
    await overview();
  }
}
async function stat(){
  const j=await(await fetch("/api/stats")).json();
  stats.innerHTML="<h2>Statystyki</h2>"+j.map(x=>`<div class="card"><h3>${esc(x.station)}</h3>${x.files} plików • ${x.size}</div>`).join("");
}
function calendarUrl(){
  const token=window.CALENDAR_TOKEN||"";
  return token?("/calendar.ics?token="+encodeURIComponent(token)):"/calendar.ics";
}

function backup(){ location="/api/backup"; }
async function importBackup(input,mode="merge"){
  const file=input.files?.[0];
  if(!file)return;
  const replacing=mode==="replace";
  const question=replacing
    ? "PRZYWRÓCIĆ backup i zastąpić całą obecną konfigurację? Najpierw zostanie utworzona kopia bezpieczeństwa."
    : "SCALIĆ importowaną konfigurację z obecną? Istniejące stacje i harmonogramy zostaną zachowane; nowe pozycje będą dopisane.";
  if(!confirm(question)){
    input.value="";
    return;
  }
  try{
    const text=await file.text();
    const r=await fetch("/api/import-backup?mode="+encodeURIComponent(mode),{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:text
    });
    const j=await r.json();
    if(!r.ok||!j.ok){
      alert("Błąd importu: "+(j.message||j.error||("HTTP "+r.status)));
      input.value="";
      return;
    }
    if(j.mode==="merge"){
      alert(`Scalanie zakończone. Stacje razem: ${j.stations}; nowe stacje: ${j.stations_added}; nowe wpisy harmonogramu: ${j.schedules_added}; duplikaty pominięte: ${j.duplicates_skipped}; konflikty pominięte: ${j.conflicts_skipped}. Kopia: ${j.backup||"zachowana"}.`);
    }else{
      alert(`Backup przywrócony: ${j.stations} stacji. Poprzednia konfiguracja: ${j.backup||"zachowana"}.`);
    }
    input.value="";
    await fullLoad();
    if(typeof renderToday==="function")renderToday();
    if(typeof renderCalendar==="function")renderCalendar();
  }catch(e){
    alert("Błąd importu: "+e);
    input.value="";
  }
}


async function overview(){
  const j=await(await fetch("/api/overview")).json();
  stStations.textContent=j.stations;
  stRecording.textContent=j.recording;
  stFiles.textContent=j.files;
  stSize.textContent=j.size;
  stFree.textContent=j.free||"—";
  if(j.disk_total_bytes){
    const pct=Math.max(0,Math.min(100,(j.disk_used_bytes/j.disk_total_bytes)*100));
    diskFill.style.width=pct.toFixed(1)+"%";
    diskText.textContent=pct.toFixed(1)+"% • "+j.disk_used+" / "+j.disk_total;
  }
  (j.station_usage||[]).forEach(x=>{
    const sel=`[data-station="${CSS.escape(x.station)}"]`;
    const text=document.querySelector(".station-storage-text"+sel);
    const fill=document.querySelector(".station-storage-fill"+sel);
    if(text) text.textContent=x.limit_bytes>0 ? `${x.size} / ${x.limit}` : `${x.size}`;
    if(fill){
      const pct=x.limit_bytes>0 ? Math.min(100,(x.bytes/x.limit_bytes)*100) : Math.min(100,x.relative_percent||0);
      fill.style.width=pct.toFixed(1)+"%";
    }
  });
}

async function loadHealth(){
  const box=document.getElementById("healthList");
  if(!box)return;
  box.innerHTML='<span class="muted">Sprawdzanie strumieni...</span>';
  try{
    const r=await fetch("/api/health",{cache:"no-store"});
    const j=await r.json();
    if(!r.ok){
      box.innerHTML=`<div class="danger">Błąd HTTP ${r.status}: ${esc(j.message||j.error||"")}</div>`;
      return;
    }
    const items=Object.entries(j.stations||{});
    if(!items.length){
      box.innerHTML='<div class="muted">Brak danych diagnostycznych. Pierwszy test może pojawić się po około minucie od startu kontenera.</div>';
      return;
    }
    box.innerHTML='<div class="health-grid">'+items.map(([name,x])=>{
      const checks=+x.checks||0, oks=+x.ok||0;
      const pct=checks?Math.round(oks/checks*100):0;
      const status=x.last_status||"unknown";
      const cls=status==="online"?"health-online":(status==="offline"?"health-offline":"health-unknown");
      return `<div class="health-card">
        <h3>${esc(name)}</h3>
        <div class="${cls}"><b>${esc(status.toUpperCase())}</b></div>
        <div class="muted">${esc(x.codec||"")} ${esc(x.format||"")}${x.bit_rate?" • "+Math.round((+x.bit_rate)/1000)+" kb/s":""}</div>
        ${x.now_playing?`<div class="nowplaying">Teraz gra: <b>${esc(x.now_playing)}</b></div>`:""}
        <div class="muted">Stabilność: ${pct}% (${oks}/${checks})</div>
        <div class="healthbar"><div style="width:${pct}%"></div></div>
        ${x.last_error?`<div class="danger">${esc(x.last_error)}</div>`:""}
        <div class="muted">Ostatni test: ${esc(x.last_check||"—")}</div>
      </div>`;
    }).join("")+'</div>';
  }catch(e){
    box.innerHTML=`<div class="danger">Nie udało się pobrać stanu strumieni: ${esc(e)}</div>`;
  }
}

async function fullLoad(){
  const x=await(await fetch("/api/data",{cache:"no-store"})).json();
  D=x;
  D.stations=D.stations||[];
  D.status=D.status||{};
  render();
  if(typeof renderToday==="function") renderToday();
  if(typeof renderCalendar==="function") renderCalendar();
  await overview();
}
async function statusLoad(){
  try{
    const x=await(await fetch("/api/data",{cache:"no-store"})).json();
    D.stations=x.stations||D.stations||[];
    D.status=x.status||{};
    D.stations.forEach((s,i)=>{
      const st=D.status[s.name]||{};
      const el=document.querySelector(`.status-${i}`);
      if(el){
        el.textContent=st.status||"—";
        el.className=`status status-${i} ${esc(st.status||"waiting")}`;
      }
    });
    if(typeof renderToday==="function") renderToday();
    if(typeof renderCalendar==="function") renderCalendar();
    await overview();
  }catch(e){
    console.error("statusLoad",e);
  }
}

function tickClocks(){
  document.querySelectorAll(".duration").forEach(x=>x.textContent=durationFrom(x.dataset.start));
  document.querySelectorAll(".countdown").forEach(x=>x.textContent="("+until(x.dataset.when)+")");
}
fullLoad();
setInterval(statusLoad,5000);
setInterval(tickClocks,1000);
</script>
</body>
</html>
"""


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

def serve(port,load,save,state,lock,ensure,test,root):
    def valid(rel):
        p=(root/unquote(rel)).resolve()
        rr=root.resolve()
        if rr not in p.parents:
            return None
        return p

    class H(BaseHTTPRequestHandler):
        def sendj(self,o,c=200):
            b=json.dumps(o,ensure_ascii=False).encode("utf-8")
            self.send_response(c)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            u=urlparse(self.path)
            q=parse_qs(u.query)

            if u.path in ("/static/favicon.svg","/favicon.ico"):
                try:
                    b=Path("/app/static/favicon.svg").read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type","image/svg+xml")
                    self.send_header("Content-Length",str(len(b)))
                    self.end_headers()
                    self.wfile.write(b)
                except Exception:
                    self.send_error(404)
                return

            if u.path=="/calendar.ics":
                token=os.getenv("CALENDAR_TOKEN","").strip()
                supplied=q.get("token",[""])[0]
                if token and supplied!=token:
                    return self.sendj({"ok":False,"message":"Unauthorized"},403)
                try:
                    import datetime as _dt
                    days_map={"mon":0,"tue":1,"wed":2,"thu":3,"fri":4,"sat":5,"sun":6}
                    byday={"mon":"MO","tue":"TU","wed":"WE","thu":"TH","fri":"FR","sat":"SA","sun":"SU"}
                    now=_dt.datetime.now()
                    monday=(now-_dt.timedelta(days=now.weekday())).date()
                    lines=["BEGIN:VCALENDAR","VERSION:2.0","CALSCALE:GREGORIAN","METHOD:PUBLISH",
                           "PRODID:-//Internet Radio Recorder//2.1.1//PL",
                           "X-WR-CALNAME:Internet Radio Recorder"]
                    for st in load():
                        if not st.get("enabled",True):
                            continue
                        for key,items in (st.get("schedule") or {}).items():
                            if key not in days_map:
                                continue
                            for raw in items:
                                if isinstance(raw,list):
                                    start,end,title=raw[0],raw[1],""
                                    pre=post=0
                                else:
                                    start=raw.get("start","00:00")
                                    end=raw.get("end","23:59")
                                    title=raw.get("title","")
                                    pre=int(raw.get("pre",0) or 0)
                                    post=int(raw.get("post",0) or 0)
                                d=monday+_dt.timedelta(days=days_map[key])
                                sh,sm=map(int,start.split(":"));eh,em=map(int,end.split(":"))
                                sdt=_dt.datetime.combine(d,_dt.time(sh,sm))-_dt.timedelta(minutes=pre)
                                edt=_dt.datetime.combine(d,_dt.time(eh,em))+_dt.timedelta(minutes=post)
                                if edt<=sdt:
                                    edt+=_dt.timedelta(days=1)
                                uid=(st.get("name","")+"-"+key+"-"+start+"-"+title).replace(" ","_").replace("@","_")
                                summary=(title or "Nagranie").replace("\n"," ").replace(",","\\,")
                                desc=(f"Stacja: {st.get('name','')} | Ramówka: {start}-{end} | pre {pre} min / post {post} min").replace(",","\\,")
                                lines += [
                                    "BEGIN:VEVENT",
                                    f"UID:{uid}@internet-radio-recorder",
                                    f"DTSTART:{sdt.strftime('%Y%m%dT%H%M%S')}",
                                    f"DTEND:{edt.strftime('%Y%m%dT%H%M%S')}",
                                    f"RRULE:FREQ=WEEKLY;BYDAY={byday[key]}",
                                    f"SUMMARY:📻 {summary}",
                                    f"DESCRIPTION:{desc}",
                                    "END:VEVENT"
                                ]
                    lines.append("END:VCALENDAR")
                    b=("\r\n".join(lines)+"\r\n").encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type","text/calendar; charset=utf-8")
                    self.send_header("Content-Disposition",'inline; filename="radio-recorder.ics"')
                    self.send_header("Cache-Control","no-cache, no-store, must-revalidate")
                    self.send_header("Content-Length",str(len(b)))
                    self.end_headers()
                    self.wfile.write(b)
                    return
                except Exception as e:
                    return self.sendj({"ok":False,"message":str(e)},500)

            if u.path=="/api/data":
                with lock:
                    return self.sendj({"stations":load(),"status":{n:{k:v for k,v in x.items() if k!="station"} for n,x in state.items()}})

            if u.path=="/api/health":
                try:
                    p=Path("/config/stream-health.json")
                    if p.exists():
                        return self.sendj(json.loads(p.read_text(encoding="utf-8")))
                    return self.sendj({"stations":{}})
                except Exception as e:
                    return self.sendj({"stations":{},"error":str(e)})

            if u.path=="/api/executions":
                try:
                    p=Path("/config/executions.json")
                    if p.exists():
                        return self.sendj(json.loads(p.read_text(encoding="utf-8")))
                    return self.sendj({"executions":[]})
                except Exception as e:
                    return self.sendj({"executions":[],"error":str(e)})

            if u.path=="/api/calendar.ics":
                try:
                    lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Internet Radio Recorder//2.0//PL"]
                    days_map={"mon":0,"tue":1,"wed":2,"thu":3,"fri":4,"sat":5,"sun":6}
                    now=__import__("datetime").datetime.now()
                    monday=(now-__import__("datetime").timedelta(days=now.weekday())).date()
                    for st in load():
                        for key,items in (st.get("schedule") or {}).items():
                            for raw in items:
                                if isinstance(raw,list):
                                    start,end,title=raw[0],raw[1],""
                                    pre=post=0
                                else:
                                    start,end,title=raw.get("start","00:00"),raw.get("end","23:59"),raw.get("title","")
                                    pre=int(raw.get("pre",0) or 0);post=int(raw.get("post",0) or 0)
                                d=monday+__import__("datetime").timedelta(days=days_map.get(key,0))
                                sh,sm=map(int,start.split(":"));eh,em=map(int,end.split(":"))
                                sdt=__import__("datetime").datetime.combine(d,__import__("datetime").time(sh,sm))-__import__("datetime").timedelta(minutes=pre)
                                edt=__import__("datetime").datetime.combine(d,__import__("datetime").time(eh,em))+__import__("datetime").timedelta(minutes=post)
                                uid=f"{st.get('name','')}-{key}-{start}-{title}".replace(" ","_")
                                lines += ["BEGIN:VEVENT",f"UID:{uid}@internet-radio-recorder",
                                          f"DTSTART:{sdt.strftime('%Y%m%dT%H%M%S')}",
                                          f"DTEND:{edt.strftime('%Y%m%dT%H%M%S')}",
                                          f"SUMMARY:{st.get('name','')} - {title or 'Nagranie'}","END:VEVENT"]
                    lines.append("END:VCALENDAR")
                    b=("\r\n".join(lines)+"\r\n").encode("utf-8")
                    self.send_response(200);self.send_header("Content-Type","text/calendar; charset=utf-8")
                    self.send_header("Content-Disposition",'attachment; filename="radio-recorder.ics"')
                    self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
                except Exception as e:
                    return self.sendj({"error":str(e)},500)

            if u.path=="/api/overview":
                total_files=0
                total_bytes=0
                for p in root.rglob("*"):
                    if p.is_file():
                        total_files+=1
                        try: total_bytes+=p.stat().st_size
                        except: pass
                with lock:
                    recording=sum(1 for x in state.values() if x.get("status")=="recording")
                try:
                    du=__import__("shutil").disk_usage(root)
                    free=human(du.free)
                    disk_total=du.total
                    disk_used=du.used
                except:
                    free="—"
                    disk_total=0
                    disk_used=0

                usage=[]
                stations_cfg=load()
                max_station_bytes=1
                raw=[]
                for st in stations_cfg:
                    d=root/st["name"].replace(" ","_")
                    # Recorder safe() also maps punctuation; find actual folder by normalized fallback.
                    candidates=[x for x in root.iterdir() if x.is_dir()] if root.exists() else []
                    match=next((x for x in candidates if x.name.lower()==d.name.lower()),None)
                    if match is None:
                        # common exact folder names from current recorder
                        import re as _re
                        sn="".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(st.get("name",""))).strip("._") or "station"
                        match=root/sn
                    b=0
                    if match.exists():
                        for p in match.rglob("*"):
                            if p.is_file():
                                try:b+=p.stat().st_size
                                except:pass
                    try:limit_gb=float(st.get("max_storage_gb",0) or 0)
                    except:limit_gb=0
                    limit_bytes=int(limit_gb*1024*1024*1024)
                    raw.append((st.get("name",""),b,limit_bytes))
                    max_station_bytes=max(max_station_bytes,b)
                for name,b,limit_bytes in raw:
                    usage.append({
                        "station":name,"bytes":b,"size":human(b),
                        "limit_bytes":limit_bytes,"limit":human(limit_bytes) if limit_bytes else "",
                        "relative_percent":round((b/max_station_bytes)*100,1)
                    })
                return self.sendj({
                    "stations":len(stations_cfg),"recording":recording,"files":total_files,
                    "size":human(total_bytes),"free":free,
                    "disk_total_bytes":disk_total,"disk_used_bytes":disk_used,
                    "disk_total":human(disk_total) if disk_total else "—",
                    "disk_used":human(disk_used) if disk_used else "—",
                    "station_usage":usage
                })

            if u.path=="/api/library":
                fs=[]
                for p in root.rglob("*"):
                    if p.is_file():
                        rel=str(p.relative_to(root))
                        parts=p.relative_to(root).parts
                        fs.append({
                            "station":parts[0] if parts else "",
                            "date":parts[1] if len(parts)>2 else "",
                            "name":p.name,
                            "path":rel,
                            "size":human(p.stat().st_size),
                            "mtime":p.stat().st_mtime
                        })
                return self.sendj({"files":sorted(fs,key=lambda x:x["mtime"],reverse=True)[:1000]})

            if u.path=="/api/stats":
                out=[]
                for d in root.iterdir() if root.exists() else []:
                    if d.is_dir():
                        files=[p for p in d.rglob("*") if p.is_file()]
                        size=sum(p.stat().st_size for p in files)
                        out.append({"station":d.name,"files":len(files),"size":human(size),"bytes":size})
                return self.sendj(out)

            if u.path=="/api/backup":
                b=json.dumps({"stations":load()},ensure_ascii=False,indent=2).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type","application/json; charset=utf-8")
                self.send_header("Content-Disposition",'attachment; filename="stations-backup.json"')
                self.send_header("Content-Length",str(len(b)))
                self.end_headers()
                self.wfile.write(b)
                return

            if u.path=="/media":
                p=valid(q.get("path",[""])[0])
                if not p or not p.is_file():
                    return self.send_error(404)
                ctype="audio/aac" if p.suffix.lower()==".aac" else ("audio/mp4" if p.suffix.lower()==".m4a" else "audio/mpeg")
                size=p.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type",ctype)
                self.send_header("Content-Length",str(size))
                if q.get("download"):
                    self.send_header("Content-Disposition",f'attachment; filename="{p.name}"')
                self.end_headers()
                with open(p,"rb") as f:
                    while True:
                        b=f.read(1024*1024)
                        if not b: break
                        self.wfile.write(b)
                return

            b=PAGE.replace("__CALENDAR_TOKEN__",os.getenv("CALENDAR_TOKEN","")).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_POST(self):
            u=urlparse(self.path)
            q=parse_qs(u.query)
            n=q.get("name",[""])[0]

            if u.path in ("/api/start","/api/stop"):
                with lock:
                    if n in state:
                        state[n]["manual"]=u.path.endswith("start")
                return self.sendj({"ok":True})

            if u.path=="/api/import-backup":
                try:
                    raw=self.rfile.read(int(self.headers.get("Content-Length","0")))
                    body=json.loads(raw or b"{}")
                    stations=body.get("stations")
                    if not isinstance(stations,list):
                        raise ValueError("Backup nie zawiera listy 'stations'.")
                    mode=(q.get("mode",["merge"])[0] or "merge").lower()
                    if mode not in ("merge","replace"):
                        raise ValueError("Nieznany tryb importu.")

                    # Zawsze zachowujemy datowaną kopię przed importem.
                    cfg=Path("/config/stations.json")
                    backup_name=""
                    if cfg.exists():
                        import datetime as _dt, shutil as _shutil
                        stamp=_dt.datetime.now().strftime("%Y%m%d-%H%M%S")
                        bp=cfg.with_name(f"stations.before-import-{stamp}.json")
                        _shutil.copy2(cfg,bp)
                        backup_name=bp.name

                    stats={"stations_added":0,"schedules_added":0,"duplicates_skipped":0,"conflicts_skipped":0}
                    if mode=="merge":
                        merged,stats=merge_station_configs(load(),stations)
                        save(merged)
                        expected=len(merged)
                    else:
                        save(stations)
                        expected=len(stations)

                    ensure()
                    reread=load()
                    if len(reread)!=expected:
                        raise IOError("Weryfikacja importu nie powiodła się.")
                    return self.sendj({
                        "ok":True,"mode":mode,"stations":len(reread),"backup":backup_name,
                        **stats
                    })
                except PermissionError as e:
                    return self.sendj({"ok":False,"message":"Brak uprawnień do /config: "+str(e)},500)
                except Exception as e:
                    return self.sendj({"ok":False,"message":str(e)},400)

            if u.path=="/api/save":
                try:
                    raw=self.rfile.read(int(self.headers.get("Content-Length","0")))
                    body=json.loads(raw or b"{}")
                    stations=body.get("stations")
                    if stations is None:
                        raise ValueError("Brak pola 'stations' w żądaniu.")
                    save(stations)
                    ensure()
                    # readback: backend potwierdza, że po zapisie widzi te same dane
                    reread=load()
                    if len(reread)!=len(stations):
                        raise IOError("Po zapisie liczba stacji w stations.json jest niezgodna.")
                    return self.sendj({"ok":True,"message":"Zapisano stations.json","stations":len(reread)})
                except PermissionError as e:
                    return self.sendj({"ok":False,"message":"Brak uprawnień do /config/stations.json: "+str(e)},500)
                except OSError as e:
                    return self.sendj({"ok":False,"message":"Błąd zapisu pliku stations.json: "+str(e)},500)
                except Exception as e:
                    return self.sendj({"ok":False,"message":str(e)},400)

            if u.path=="/api/test":
                try:
                    body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
                    return self.sendj(test(body.get("url","")))
                except Exception as e:
                    return self.sendj({"ok":False,"message":str(e)},400)

            if u.path=="/api/delete":
                p=valid(q.get("path",[""])[0])
                if not p or not p.is_file():
                    return self.sendj({"ok":False},404)
                p.unlink()
                return self.sendj({"ok":True})

            return self.sendj({"ok":False},404)

        def log_message(self,*a):
            pass

    ThreadingHTTPServer(("0.0.0.0",port),H).serve_forever()
