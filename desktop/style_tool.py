#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.11.04
# =====================================================================
"""
style_tool.py — 设置页（改提醒的样子 + 多久查一次 + 看一眼当前状态）
=====================================================================

为什么要它：
  以前想换风格得重跑安装包（重装 590 多个文件），想改检查频率只能敲命令行，
  想看"现在到底设成什么样"也只能敲 `--status`。这个页面把这三件事收到一起：
  双击即开 → 看着状态改 → 点保存 → 自动关掉。

设计 / Design:
  - 零第三方依赖（仅 Python 标准库）
  - 本地 http.server 起一个只在本机可见的页面（127.0.0.1:8766~8775）
  - 外观 → 直接写同目录 config.json
  - 检查频率 → 调用 deepseek_price_alert.py 的 --setup-schedule / --every /
    --remove-schedule，真正的计划任务由主脚本去建（这里不重复实现一遍逻辑）
  - 页面关掉后服务自己退出；开太久没人管也会自己退（20 分钟）

只提供主脚本真正会读取的三项外观：
  terminal_style / price_unit / reminder_channel
（notification_style 与 window_theme 主脚本未读取，故不提供，免得选了却不生效）

用法 / Usage:
  双击安装根目录的「设置.bat」，或直接：
  python style_tool.py

原创使用许可 (Original Works License).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import json
import subprocess
import sys
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
HISTORY_FILE = BASE_DIR / "price_history.json"
MAIN_SCRIPT = BASE_DIR / "deepseek_price_alert.py"

# 与 deepseek_price_alert.py 的 load_config() 默认值保持一致
DEFAULTS = {
    "notification_style": "clean",
    "terminal_style": "log",
    "window_theme": "light",
    "price_unit": "auto",
    "reminder_channel": "popup",
    "schedule_mode": "off",
    "schedule_every": 0,
    "schedule_time": "",
}

# 只有主脚本真正读取的外观项才允许改
CHOICES = {
    "terminal_style": ("log", "table", "compact", "color"),
    "price_unit": ("auto", "usd_per_1m", "cny_per_10k", "cny_per_1m"),
    "reminder_channel": ("popup", "popup_sound"),
}

# 频率：向导/命令行都只用能整除 24 的值，每天触发时刻才固定
EVERY_CHOICES = (2, 3, 4, 6, 8, 12)
DEFAULT_TIME = "09:30"
IDLE_QUIT_SECONDS = 20 * 60

PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>设置 — DeepSeek 降价提醒</title>
<style>
  :root{--bg:#0f1115;--panel:#1a1d24;--panel2:#21252f;--bd:#2c313d;--tx:#e8eaed;
        --mu:#9aa3b2;--ac:#4f7cff;--ac2:#7aa2ff;--gr:#3fb97f;--rd:#e5534b}
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,
       "Segoe UI","Microsoft YaHei",sans-serif;min-height:100vh;display:flex;
       align-items:flex-start;justify-content:center;padding:36px 16px}
  .wrap{max-width:820px;width:100%}
  header{text-align:center;margin-bottom:22px}
  h1{font-size:22px;font-weight:700}
  header p{color:var(--mu);font-size:13px;margin-top:8px;line-height:1.7}

  /* 状态条：只读，一眼看清现在是什么样 */
  .status{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;
          background:var(--panel);border:1px solid var(--bd);border-radius:12px;
          padding:14px 16px;margin-bottom:14px}
  .si{min-width:0}
  .si .k{font-size:11px;color:var(--mu);letter-spacing:.5px}
  .si .v{font-size:13px;font-weight:700;margin-top:4px;line-height:1.4;word-break:break-all}
  .si .v.on{color:var(--gr)}
  .si .v.off{color:var(--mu)}
  .si .sub{font-size:10px;color:var(--mu);margin-top:3px}

  .grp{background:var(--panel);border:1px solid var(--bd);border-radius:12px;
       padding:18px 20px;margin-bottom:14px}
  .gt{font-size:13px;font-weight:700;color:var(--ac2);display:flex;align-items:center;gap:8px}
  .gt .tag{font-size:10px;color:var(--mu);border:1px solid var(--bd);border-radius:999px;
           padding:1px 7px;font-weight:400}
  .gs{font-size:12px;color:var(--mu);margin:4px 0 12px;line-height:1.6}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:10px}
  .card{background:var(--panel2);border:2px solid var(--bd);border-radius:10px;
        padding:10px 12px;cursor:pointer;transition:border-color .15s,box-shadow .15s}
  .card:hover{border-color:var(--ac2)}
  .card.sel{border-color:var(--ac);box-shadow:0 0 0 3px rgba(79,124,255,.18)}
  .nm{display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:700}
  .ck{color:var(--gr);font-size:12px}
  .ds{font-size:11px;color:var(--mu);margin:3px 0 8px;line-height:1.5}
  .pv{border-radius:6px;overflow:hidden;font-family:Consolas,"Cascadia Code",monospace;
      font-size:10px;line-height:1.55;border:1px solid transparent}
  .pv-t{background:#0a0c10;color:#d4d4d4;padding:7px 8px;white-space:pre-line}
  .pv-u{background:#f8f8f8;border-color:#e0e0e0;color:#333;padding:7px 8px;text-align:center}
  .pv-s{display:flex;align-items:center;gap:6px;color:var(--mu);font-size:11px;padding:6px 0;
        font-family:-apple-system,"Microsoft YaHei",sans-serif}

  .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:12px;
       font-size:13px;color:var(--mu)}
  .row.hide{display:none}
  input[type="time"]{background:var(--panel2);border:1px solid var(--bd);color:var(--tx);
       border-radius:6px;padding:5px 8px;font-size:13px;font-family:inherit}
  .chips{display:flex;gap:8px;flex-wrap:wrap}
  .chip{background:var(--panel2);border:1px solid var(--bd);color:var(--tx);border-radius:999px;
        padding:5px 14px;font-size:12px;cursor:pointer;transition:all .15s}
  .chip:hover{border-color:var(--ac2)}
  .chip.sel{background:rgba(79,124,255,.18);border-color:var(--ac);color:#fff}

  .bar{text-align:center;margin-top:22px}
  button{background:var(--ac);color:#fff;border:none;border-radius:8px;padding:14px 42px;
         font-size:16px;font-weight:600;cursor:pointer;transition:background .15s}
  button:hover{background:var(--ac2)}
  button:disabled{opacity:.5;cursor:not-allowed}
  button.ghost{background:transparent;color:var(--mu);border:1px solid var(--bd);
         padding:13px 24px;font-size:13px;font-weight:500;margin-left:10px}
  button.ghost:hover{color:var(--tx);border-color:var(--ac2);background:transparent}
  .st{margin-top:16px;font-size:14px;min-height:22px;color:var(--mu);line-height:1.8;
      text-align:left;white-space:pre-wrap}
  .st.ok{color:var(--gr)}
  .st.err{color:var(--rd)}
  .raw{margin-top:10px;background:#0a0c10;border:1px solid var(--bd);border-radius:8px;
       padding:10px 12px;font-family:Consolas,monospace;font-size:11px;color:#a8b2c1;
       white-space:pre-wrap;word-break:break-all;display:none;max-height:180px;overflow:auto}
  .note{margin-top:18px;padding:10px 12px;background:var(--panel2);border:1px solid var(--bd);
        border-left:3px solid var(--ac);border-radius:0 8px 8px 0;font-size:12px;
        color:var(--mu);line-height:1.8}
  code{background:#0a0c10;border:1px solid var(--bd);border-radius:4px;padding:1px 5px;
       font-family:Consolas,monospace;font-size:11px;color:#a8b2c1}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>⚙️ 设置</h1>
    <p>改完点保存就行，不会重装任何程序，价格历史也不受影响。</p>
  </header>

  <div class="status" id="status"></div>

  <!-- 检查频率 -->
  <div class="grp">
    <div class="gt">⏰ 多久查一次价格 <span class="tag">会建系统计划任务</span></div>
    <div class="gs">只在电脑开着的时候才会跑；关机或睡眠期间那一次会错过。</div>
    <div class="grid" id="g-mode"></div>
    <div class="row" id="row-every">
      <span>每隔多久：</span><div class="chips" id="chips"></div>
    </div>
    <div class="row" id="row-time">
      <span id="lbl-time">每天几点查：</span>
      <input type="time" id="t-time" value="09:30">
      <span style="font-size:11px">（按你电脑的本地时间）</span>
    </div>
  </div>

  <!-- 外观 -->
  <div class="grp">
    <div class="gt">📟 终端输出</div>
    <div class="gs">在命令行里跑的时候，价格信息排成什么样。</div>
    <div class="grid" id="g-term"></div>
  </div>

  <div class="grp">
    <div class="gt">💰 价格显示单位</div>
    <div class="gs">同一个价格，用哪种口径讲给你听。</div>
    <div class="grid" id="g-unit"></div>
  </div>

  <div class="grp">
    <div class="gt">🔔 提醒方式</div>
    <div class="gs">降价弹窗出现时，要不要同时响一声。</div>
    <div class="grid" id="g-ch"></div>
  </div>

  <div class="bar">
    <button id="btn" onclick="save()">保存并生效</button>
    <button class="ghost" onclick="quit()">看完了，关掉</button>
    <div class="st" id="st"></div>
    <div class="raw" id="raw"></div>
  </div>

  <div class="note">
    ℹ️ 上面「下次检查」是<b>按当前设置推算</b>的，不是从 Windows 里读出来的真实触发器——
    如果你在系统「任务计划程序」里手动改过，以那边的为准。<br>
    弹窗的<b>外观</b>由 Windows 系统决定（本工具用的是系统原生弹窗），所以这里不提供颜色选择——
    选了也不会生效，就不骗你了。<br>
    想看 12 种弹窗 / 终端 / 主题长什么样，打开工具文件夹里的 <code>style_preview.html</code>。
  </div>
</div>

<script>
const TERM = {
  log:     {n:"日志 Log",     s:"日志", d:"[时间] 消息，最常规",
            p:"[2026-11-04 09:00:00] 价格无下降变化\n[2026-11-04 09:00:00] 检查完成"},
  table:   {n:"表格 Table",   s:"表格", d:"带竖线的对齐列",
            p:"| 2026-11-04 09:00 | 价格无下降 |\n| deepseek-flash   | $0.6/1M    |"},
  compact: {n:"紧凑 Compact", s:"紧凑", d:"无时间戳，最短",
            p:"no price drop\ncheck finished"}
};
const UNIT = {
  auto:        {n:"自动 Auto",     s:"自动",   d:"美元 + 人民币都显示", p:"$0.6/1M = ¥0.0426/万"},
  usd_per_1m:  {n:"$ / 百万token", s:"美元",   d:"官方美元口径",       p:"$0.6/1M"},
  cny_per_10k: {n:"¥ / 万token",   s:"万元",   d:"人民币，最直观",     p:"¥0.0426/万token"},
  cny_per_1m:  {n:"¥ / 百万token", s:"百万元", d:"人民币，官方口径",   p:"¥4.26/百万token"}
};
const CH = {
  popup:       {n:"只弹窗",      s:"仅弹窗", d:"安静，只出现通知窗口", i:"🔇"},
  popup_sound: {n:"弹窗 + 声音", s:"带响声", d:"同时响一声系统提示音", i:"🔔"}
};
const MODE = {
  off:   {n:"先不设",     d:"不建定时任务，只靠开机自启"},
  daily: {n:"每天查一次", d:"每天固定一个时刻查，最省事"},
  every: {n:"每 N 小时",  d:"一天查好几回，大额降价能早发现"}
};

let cur = {terminal_style:"log", price_unit:"auto", reminder_channel:"popup"};
let sched = {mode:"off", every:4, time:"09:30"};
let hours = [2,3,4,6,8,12];
let touchedStyle = false;
let touchedSched = false;
let status = {};

function card(sel, name, desc, pv){
  const el = document.createElement('div');
  el.className = 'card' + (sel ? ' sel' : '');
  el.innerHTML = '<div class="nm"><span>'+name+'</span>'+(sel?'<span class="ck">✔</span>':'')+'</div>'
               + '<div class="ds">'+desc+'</div>' + pv;
  return el;
}

function renderStatus(){
  const box = document.getElementById('status');
  const s = status || {};
  const items = [];

  // 定时检查
  let freq = '未设置';
  if (s.schedule_mode === 'every' && s.schedule_every > 0) {
    freq = '每 ' + s.schedule_every + ' 小时';
  } else if (s.schedule_mode === 'daily' && s.schedule_time) {
    freq = '每天 ' + s.schedule_time;
  }
  items.push('<div class="si"><div class="k">定时检查</div><div class="v '
    + (freq === '未设置' ? 'off' : '') + '">' + freq + '</div>'
    + (s.schedule_mode === 'every' && s.schedule_time ? '<div class="sub">起点 ' + s.schedule_time + '</div>' : '')
    + '</div>');

  // 下次检查
  items.push('<div class="si"><div class="k">下次检查</div><div class="v">'
    + (s.next_run || '—') + '</div><div class="sub">按当前设置推算</div></div>');

  // 开机自启
  items.push('<div class="si"><div class="k">开机自启</div><div class="v '
    + (s.startup ? 'on' : 'off') + '">' + (s.startup ? '开' : '关') + '</div></div>');

  // 上次检查
  items.push('<div class="si"><div class="k">上次检查</div><div class="v">'
    + (s.last_checked || '还没查过') + '</div>'
    + (s.task_exists === false && s.schedule_mode !== 'off'
        ? '<div class="sub" style="color:#e5a44b">系统里还没这个任务，保存一次就会建好</div>' : '')
    + '</div>');

  box.innerHTML = items.join('');
}

function renderSched(){
  const g = document.getElementById('g-mode');
  g.innerHTML = '';
  Object.entries(MODE).forEach(([k,v])=>{
    const sel = sched.mode === k;
    const el = card(sel, v.n, v.d, '');
    el.onclick = ()=>{ sched.mode = k; touchedSched = true; renderSched(); };
    g.appendChild(el);
  });

  const c = document.getElementById('chips');
  c.innerHTML = '';
  hours.forEach(h=>{
    const b = document.createElement('div');
    b.className = 'chip' + (sched.every === h ? ' sel' : '');
    b.textContent = '每 ' + h + ' 小时';
    b.onclick = ()=>{ sched.every = h; touchedSched = true; renderSched(); };
    c.appendChild(b);
  });

  document.getElementById('row-every').classList.toggle('hide', sched.mode !== 'every');
  const showTime = (sched.mode === 'daily' || sched.mode === 'every');
  document.getElementById('row-time').classList.toggle('hide', !showTime);
  document.getElementById('lbl-time').textContent =
    sched.mode === 'every' ? '从几点开始算：' : '每天几点查：';
  const ti = document.getElementById('t-time');
  if (document.activeElement !== ti) ti.value = sched.time;
}

function renderStyle(){
  const gt = document.getElementById('g-term'); gt.innerHTML='';
  Object.entries(TERM).forEach(([k,v])=>{
    const el = card(cur.terminal_style===k, v.n, v.d, '<div class="pv pv-t">'+v.p+'</div>');
    el.onclick=()=>{cur.terminal_style=k;touchedStyle=true;renderStyle();};
    gt.appendChild(el);
  });
  const gu = document.getElementById('g-unit'); gu.innerHTML='';
  Object.entries(UNIT).forEach(([k,v])=>{
    const el = card(cur.price_unit===k, v.n, v.d, '<div class="pv pv-u">'+v.p+'</div>');
    el.onclick=()=>{cur.price_unit=k;touchedStyle=true;renderStyle();};
    gu.appendChild(el);
  });
  const gc = document.getElementById('g-ch'); gc.innerHTML='';
  Object.entries(CH).forEach(([k,v])=>{
    const pv = '<div class="pv pv-s"><span style="font-size:14px">'+v.i+'</span><span>降价时'
             + (k==='popup'?'不发声':'响一声') + '</span></div>';
    const el = card(cur.reminder_channel===k, v.n, v.d, pv);
    el.onclick=()=>{cur.reminder_channel=k;touchedStyle=true;renderStyle();};
    gc.appendChild(el);
  });
}

async function load(){
  try{
    const r = await fetch('/api/current');
    const d = await r.json();
    if (d.config) cur = d.config;
    if (d.hours) hours = d.hours;
    status = d.status || {};
    sched.mode = status.schedule_mode || 'off';
    sched.every = status.schedule_every || 4;
    sched.time = status.schedule_time || '09:30';
    if (!hours.includes(sched.every)) sched.every = 4;
  }catch(e){}
  document.getElementById('t-time').value = sched.time;
  renderStatus(); renderSched(); renderStyle();
}

document.getElementById('t-time').addEventListener('change', (e)=>{
  sched.time = e.target.value || '09:30';
  touchedSched = true;
});

let closeTimer = null;

async function save(){
  const btn = document.getElementById('btn');
  const st = document.getElementById('st');
  const raw = document.getElementById('raw');
  btn.disabled = true;
  raw.style.display = 'none';
  st.className = 'st'; st.textContent = '⏳ 正在保存…';

  const payload = {};
  if (touchedStyle) payload.style = cur;
  if (touchedSched) payload.schedule = {
    mode: sched.mode, every: sched.every,
    time: document.getElementById('t-time').value || '09:30'
  };
  if (!touchedStyle && !touchedSched) {
    st.textContent = '你还没改任何东西。改一项再点保存，或者点「看完了，关掉」。';
    btn.disabled = false;
    return;
  }

  try{
    const r = await fetch('/api/save', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    if (!d.ok){
      btn.disabled = false;
      st.className = 'st err';
      st.textContent = '❌ 保存失败：' + (d.error || '未知错误');
      return;
    }

    const lines = [];
    if (d.style_saved) lines.push('✅ 外观已保存 → ' + d.config_path);
    if (d.schedule) {
      const s = d.schedule;
      if (s.mode === 'off') lines.push('✅ 定时检查已关闭');
      else if (s.ok) lines.push('✅ 定时检查已设置：' + s.summary);
      else lines.push('⚠️ 外观已保存，但定时任务没设上：' + (s.error || '未知原因'));
      if (s.output) { raw.style.display = 'block'; raw.textContent = s.output; }
    }
    const bad = d.schedule && d.schedule.mode && !d.schedule.ok && d.schedule.mode !== 'off';
    st.className = 'st ' + (bad ? 'err' : 'ok');
    st.textContent = lines.join('\n') + (bad ? '\n\n可以截图把上面那段给我看。' : '\n\n这个窗口会在 5 秒后自动关闭。');
    btn.textContent = '已保存';
    if (!bad) {
      let left = 5;
      closeTimer = setInterval(()=>{
        left -= 1;
        if (left <= 0) { clearInterval(closeTimer); quit(); }
      }, 1000);
    }
  }catch(e){
    btn.disabled = false;
    st.className = 'st err';
    st.textContent = '❌ 连不上本地服务，可能已经关掉了。重新双击「设置.bat」即可。';
  }
}

async function quit(){
  try { await fetch('/api/quit', {method:'POST'}); } catch(e){}
  document.body.innerHTML = '<div style="text-align:center;padding:60px;color:#9aa3b2;'
    + 'font-family:-apple-system,sans-serif;font-size:15px">已关闭，可以关掉这个页面了。</div>';
}

load();
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# 配置读写 / Config
# --------------------------------------------------------------------------
def load_config() -> dict:
    """读现有 config.json，缺失字段用默认值补齐（不丢用户其它字段）。"""
    cfg = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def normalize_style(payload) -> dict:
    """只收白名单内的合法值；非法值保持原值，不报错。"""
    cfg = load_config()
    if not isinstance(payload, dict):
        return cfg
    for key, allowed in CHOICES.items():
        val = payload.get(key)
        if isinstance(val, str) and val in allowed:
            cfg[key] = val
    return cfg


def normalize_schedule(payload):
    """校验频率。非法一律返回 None（当作没提交，不动已有任务）。"""
    if not isinstance(payload, dict):
        return None
    mode = payload.get("mode")
    if mode not in ("off", "daily", "every"):
        return None
    if mode == "off":
        return {"mode": "off", "every": 0, "time": ""}

    time_str = str(payload.get("time") or DEFAULT_TIME).strip()
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        time_str = DEFAULT_TIME

    if mode == "daily":
        return {"mode": "daily", "every": 0, "time": time_str}

    try:
        every = int(payload.get("every"))
    except (TypeError, ValueError):
        return None
    if not (1 <= every <= 23):
        return None
    return {"mode": "every", "every": every, "time": time_str}


# --------------------------------------------------------------------------
# 状态 / Status（只读：频率、上次检查、开机自启、推算下次）
# --------------------------------------------------------------------------
def _startup_enabled() -> bool:
    try:
        startup_dir = (Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows"
                       / "Start Menu" / "Programs" / "Startup")
        return (startup_dir / "deepseek_price_alert.vbs").exists()
    except Exception:
        return False


def _task_exists(task_name: str = "DeepSeekPriceAlertDaily") -> bool:
    """通过注册表 TaskCache 判断计划任务是否存在（不调用 schtasks）。"""
    if not sys.platform.startswith("win"):
        return False
    try:
        import winreg
        path = r"Software\Microsoft\Windows\CurrentVersion\Schedule\TaskCache\Tree\\" + task_name
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path):
            return True
    except Exception:
        return False


def _last_checked() -> str:
    if not HISTORY_FILE.exists():
        return ""
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    raw = str(data.get("last_checked") or "")
    # 形如 2026-11-04 05:12:00 → 11-04 05:12，状态栏地方小
    return raw[5:16] if len(raw) >= 16 else raw


def _next_run(mode: str, every: int, time_str: str) -> str:
    """按「起点 + 每 N 小时」推算下次触发时刻（只是推算，非真实触发器）。"""
    if mode not in ("daily", "every") or not time_str:
        return ""
    try:
        hh, mm = (int(x) for x in time_str.split(":"))
    except ValueError:
        return ""

    now = datetime.now()
    try:
        nxt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    except ValueError:
        return ""

    if mode == "daily":
        if nxt <= now:
            nxt += timedelta(days=1)
        return nxt.strftime("%m-%d %H:%M")

    if every <= 0:
        return ""
    step = timedelta(hours=every)
    guard = 0
    while nxt <= now and guard < 500:
        nxt += step
        guard += 1
    return nxt.strftime("%m-%d %H:%M")


def collect_status() -> dict:
    cfg = load_config()
    mode = cfg.get("schedule_mode", "off")
    every = cfg.get("schedule_every", 0)
    when = cfg.get("schedule_time", "")
    if not isinstance(every, int):
        every = 0
    return {
        "schedule_mode": mode if mode in ("off", "daily", "every") else "off",
        "schedule_every": every,
        "schedule_time": when,
        "next_run": _next_run(mode, every, when),
        "startup": _startup_enabled(),
        "task_exists": _task_exists(),
        "last_checked": _last_checked(),
    }


# --------------------------------------------------------------------------
# 真正去建/删计划任务（交给主脚本做，不重复实现）
# --------------------------------------------------------------------------
def _python_exe() -> str:
    bundled = BASE_DIR / "python" / "python.exe"
    return str(bundled) if bundled.exists() else sys.executable


def apply_schedule(sched: dict) -> dict:
    if sched["mode"] == "off":
        cmd = [_python_exe(), str(MAIN_SCRIPT), "--remove-schedule"]
        summary = "已取消"
    elif sched["mode"] == "daily":
        cmd = [_python_exe(), str(MAIN_SCRIPT), "--setup-schedule", sched["time"]]
        summary = "每天 " + sched["time"]
    else:
        cmd = [_python_exe(), str(MAIN_SCRIPT), "--every", str(sched["every"]),
               "--at", sched["time"]]
        summary = "每 {} 小时（{} 起）".format(sched["every"], sched["time"])

    out = {"mode": sched["mode"], "ok": False, "summary": summary,
           "error": "", "output": "", "cmd": " ".join(cmd[1:])}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=90)
        text = ((r.stdout or "") + (r.stderr or "")).strip()
        out["ok"] = r.returncode == 0
        out["output"] = text
        if not out["ok"]:
            out["error"] = text.splitlines()[-1] if text else "退出码 {}".format(r.returncode)
    except Exception as exc:
        out["error"] = str(exc)
    return out


# --------------------------------------------------------------------------
# HTTP 服务
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "DeepSeekPriceAlertSettings/2.0"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_page(self):
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_page()
        elif self.path == "/api/current":
            cfg = load_config()
            self._json({
                "config": {k: cfg.get(k, DEFAULTS[k]) for k in CHOICES},
                "choices": {k: list(v) for k, v in CHOICES.items()},
                "hours": list(EVERY_CHOICES),
                "status": collect_status(),
                "config_path": str(CONFIG_FILE),
            })
        elif self.path == "/api/quit":
            self._json({"ok": True})
            threading.Timer(0.2, self.server.shutdown).start()
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/quit":
            self._json({"ok": True})
            threading.Timer(0.2, self.server.shutdown).start()
            return

        if self.path != "/api/save":
            self._json({"error": "not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            self._json({"ok": False, "error": "无效请求: {}".format(exc)}, 400)
            return
        if not isinstance(payload, dict):
            payload = {}

        # 外观（兼容老页面：直接把三个字段平铺在顶层）
        style_payload = payload.get("style")
        if not isinstance(style_payload, dict):
            style_payload = {k: payload[k] for k in CHOICES if k in payload} or None

        resp = {"ok": True, "style_saved": False, "config_path": str(CONFIG_FILE),
                "schedule": None}

        if style_payload:
            cfg = normalize_style(style_payload)
            try:
                CONFIG_FILE.write_text(
                    json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                resp["style_saved"] = True
                print("[settings] 外观已保存 / Style saved")
            except OSError as exc:
                self._json({"ok": False, "error": "写入失败: {}".format(exc)}, 500)
                return

        sched = normalize_schedule(payload.get("schedule"))
        if sched:
            print("[settings] 应用频率 / Apply schedule: {}".format(sched))
            resp["schedule"] = apply_schedule(sched)

        if not resp["style_saved"] and resp["schedule"] is None:
            self._json({"ok": False, "error": "没有收到任何要保存的内容"}, 400)
            return

        # 状态变了，页面关掉前不用刷新；直接返回
        resp["status"] = collect_status()
        self._json(resp)


def main() -> int:
    if not MAIN_SCRIPT.exists():
        print("=" * 60)
        print("[提示] 这个目录里没找到 deepseek_price_alert.py。")
        print("       当前目录：{}".format(BASE_DIR))
        print("       请把本文件放在工具的 desktop 文件夹里再运行。")
        print("=" * 60)
        return 1

    server = None
    port = 0
    for candidate in range(8766, 8776):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        print("[错误] 8766~8775 端口都被占用，无法启动。关掉重试一次。")
        return 2

    url = "http://127.0.0.1:{}/".format(port)
    print("=" * 60)
    print("  设置 / Settings")
    print("  配置文件：{}".format(CONFIG_FILE))
    print("  页面地址：{}".format(url))
    print("  改完点「保存并生效」；不想改了点「看完了，关掉」。")
    print("  （{} 分钟没人操作会自动关掉，不留后台进程）".format(IDLE_QUIT_SECONDS // 60))
    print("=" * 60)

    try:
        subprocess.Popen(["cmd", "/c", "start", "", url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception:
            print("请手动在浏览器打开：{}".format(url))

    # 没人管就自己退，不留一个看不见的进程占着端口
    idle = threading.Timer(IDLE_QUIT_SECONDS, server.shutdown)
    idle.daemon = True
    idle.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        idle.cancel()
    print("已退出。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
