#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.11.04
# =====================================================================
"""
style_tool.py — 改提醒的样子（轻量修改 config.json，不重装任何文件）
=====================================================================

为什么要它：
  以前想换风格，只能重新跑一遍安装包（会重装 592 个文件），
  或者手动去改 config.json（要记字段名）。
  这个小工具双击即开、选完即存，只动 config.json 一个文件。

设计 / Design:
  - 零第三方依赖（仅 Python 标准库）
  - 本地 http.server 起一个只在本机可见的页面（127.0.0.1）
  - 页面里选完点保存 → POST 回来 → 直接写同目录的 config.json
  - 保存成功后自动关掉服务，不留后台进程

只提供主脚本真正会读取的三项：
  terminal_style / price_unit / reminder_channel
（notification_style 与 window_theme 主脚本未读取，故不提供，
  免得选了却不生效）

用法 / Usage:
  双击安装根目录的「改风格.bat」，或直接：
  python style_tool.py

原创使用许可 (Original Works License).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

# 与 deepseek_price_alert.py 的 load_config() 默认值保持一致
DEFAULTS = {
    "notification_style": "clean",
    "terminal_style": "log",
    "window_theme": "light",
    "price_unit": "auto",
    "reminder_channel": "popup",
}

# 只有主脚本真正读取的项才允许改
CHOICES = {
    "terminal_style": ("log", "table", "compact", "color"),
    "price_unit": ("auto", "usd_per_1m", "cny_per_10k", "cny_per_1m"),
    "reminder_channel": ("popup", "popup_sound"),
}

PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>改提醒的样子 — DeepSeek 降价提醒</title>
<style>
  :root{--bg:#0f1115;--panel:#1a1d24;--panel2:#21252f;--bd:#2c313d;--tx:#e8eaed;
        --mu:#9aa3b2;--ac:#4f7cff;--ac2:#7aa2ff;--gr:#3fb97f;--rd:#e5534b}
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,
       "Segoe UI","Microsoft YaHei",sans-serif;min-height:100vh;display:flex;
       align-items:flex-start;justify-content:center;padding:40px 16px}
  .wrap{max-width:820px;width:100%}
  header{text-align:center;margin-bottom:14px}
  h1{font-size:22px;font-weight:700}
  header p{color:var(--mu);font-size:14px;margin-top:8px;line-height:1.7}
  .cur{text-align:center;font-size:12px;color:var(--mu);margin-bottom:24px}
  .cur b{color:var(--ac2);font-weight:600}
  .grp{background:var(--panel);border:1px solid var(--bd);border-radius:12px;
       padding:18px 20px;margin-bottom:14px}
  .gt{font-size:13px;font-weight:700;color:var(--ac2)}
  .gs{font-size:12px;color:var(--mu);margin:3px 0 12px;line-height:1.6}
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
  .bar{text-align:center;margin-top:22px}
  button{background:var(--ac);color:#fff;border:none;border-radius:8px;padding:14px 46px;
         font-size:16px;font-weight:600;cursor:pointer;transition:background .15s}
  button:hover{background:var(--ac2)}
  button:disabled{opacity:.5;cursor:not-allowed}
  .st{margin-top:16px;font-size:14px;min-height:22px;color:var(--mu);line-height:1.7}
  .st.ok{color:var(--gr)}
  .st.err{color:var(--rd)}
  .note{margin-top:20px;padding:10px 12px;background:var(--panel2);border:1px solid var(--bd);
        border-left:3px solid var(--ac);border-radius:0 8px 8px 0;font-size:12px;
        color:var(--mu);line-height:1.8}
  code{background:#0a0c10;border:1px solid var(--bd);border-radius:4px;padding:1px 5px;
       font-family:Consolas,monospace;font-size:11px;color:#a8b2c1}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🎨 改提醒的样子</h1>
    <p>只改配置文件，不会重装任何程序，价格历史也不受影响。</p>
  </header>
  <div class="cur" id="cur"></div>

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
    <div class="st" id="st">选好就点保存，改完立刻生效，下次提醒就用新的样子。</div>
  </div>

  <div class="note">
    ℹ️ 弹窗的<b>外观</b>由 Windows 系统决定（本工具用的是系统原生弹窗），所以这里不提供颜色选择——
    选了也不会生效，就不骗你了。<br>
    想看你设计的 12 种弹窗 / 终端 / 主题长什么样，打开工具文件夹里的 <code>style_preview.html</code> 就能看。
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

let cur = {terminal_style:"log", price_unit:"auto", reminder_channel:"popup"};

function card(sel, name, desc, pv){
  const el = document.createElement('div');
  el.className = 'card' + (sel ? ' sel' : '');
  el.innerHTML = '<div class="nm"><span>'+name+'</span>'+(sel?'<span class="ck">✔</span>':'')+'</div>'
               + '<div class="ds">'+desc+'</div>' + pv;
  return el;
}

function render(){
  const gt = document.getElementById('g-term'); gt.innerHTML='';
  Object.entries(TERM).forEach(([k,v])=>{
    const sel = cur.terminal_style===k;
    const el = card(sel,v.n,v.d,'<div class="pv pv-t">'+v.p+'</div>');
    el.onclick=()=>{cur.terminal_style=k;render();};
    gt.appendChild(el);
  });
  const gu = document.getElementById('g-unit'); gu.innerHTML='';
  Object.entries(UNIT).forEach(([k,v])=>{
    const sel = cur.price_unit===k;
    const el = card(sel,v.n,v.d,'<div class="pv pv-u">'+v.p+'</div>');
    el.onclick=()=>{cur.price_unit=k;render();};
    gu.appendChild(el);
  });
  const gc = document.getElementById('g-ch'); gc.innerHTML='';
  Object.entries(CH).forEach(([k,v])=>{
    const sel = cur.reminder_channel===k;
    const pv = '<div class="pv pv-s"><span style="font-size:14px">'+v.i+'</span><span>降价时'
             + (k==='popup'?'不发声':'响一声') + '</span></div>';
    const el = card(sel,v.n,v.d,pv);
    el.onclick=()=>{cur.reminder_channel=k;render();};
    gc.appendChild(el);
  });
  document.getElementById('cur').innerHTML =
    '当前：<b>' + TERM[cur.terminal_style].s + ' · ' + UNIT[cur.price_unit].s
    + ' · ' + CH[cur.reminder_channel].s + '</b>';
}

async function load(){
  try{
    const r = await fetch('/api/current');
    const d = await r.json();
    if (d.config) cur = d.config;
  }catch(e){}
  render();
}

async function save(){
  const btn = document.getElementById('btn');
  const st = document.getElementById('st');
  btn.disabled = true;
  st.className = 'st'; st.textContent = '⏳ 正在保存…';
  try{
    const r = await fetch('/api/save', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(cur)
    });
    const d = await r.json();
    if (d.ok){
      st.className = 'st ok';
      st.innerHTML = '✅ 已保存！<br>' + d.path + '<br>可以关掉这个页面了，下次提醒就用新的样子。';
      btn.textContent = '已保存';
    } else {
      btn.disabled = false;
      st.className = 'st err';
      st.textContent = '❌ 保存失败：' + (d.error || '未知错误');
    }
  }catch(e){
    btn.disabled = false;
    st.className = 'st err';
    st.textContent = '❌ 连不上本地服务，可能已经关掉了。重新双击「改风格.bat」即可。';
  }
}

load();
</script>
</body>
</html>
"""


def load_config() -> dict:
    """读现有 config.json，缺失字段用默认值补齐。"""
    cfg = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def normalize(payload: dict) -> dict:
    """只收白名单内的合法值；非法的保持原值，不报错。"""
    cfg = load_config()
    for key, allowed in CHOICES.items():
        val = payload.get(key)
        if isinstance(val, str) and val in allowed:
            cfg[key] = val
    return cfg


class Handler(BaseHTTPRequestHandler):
    server_version = "DeepSeekPriceAlertStyleTool/1.0"

    def log_message(self, fmt, *args):  # 安静一点，别刷屏
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/current":
            cfg = load_config()
            self._json({
                "config": {k: cfg[k] for k in CHOICES},
                "choices": {k: list(v) for k, v in CHOICES.items()},
                "config_path": str(CONFIG_FILE),
            })
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/save":
            self._json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            self._json({"ok": False, "error": f"无效请求: {exc}"}, 400)
            return

        cfg = normalize(payload if isinstance(payload, dict) else {})
        try:
            CONFIG_FILE.write_text(
                json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as exc:
            self._json({"ok": False, "error": f"写入失败: {exc}"}, 500)
            return

        print(f"[style] 已保存 / Saved: {CONFIG_FILE}")
        self._json({"ok": True, "path": str(CONFIG_FILE), "config": cfg})
        # 保存成功后稍等片刻再关服务，让页面能把提示显示出来
        threading.Timer(1.5, self.server.shutdown).start()


def main() -> int:
    if not (BASE_DIR / "deepseek_price_alert.py").exists():
        print("=" * 60)
        print("[提示] 这个目录里没找到 deepseek_price_alert.py。")
        print(f"       当前目录：{BASE_DIR}")
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

    url = f"http://127.0.0.1:{port}/"
    print("=" * 60)
    print("  改提醒的样子 / Change Style")
    print(f"  配置文件：{CONFIG_FILE}")
    print(f"  页面地址：{url}")
    print("  选完点「保存并生效」，这个窗口会自动关闭。")
    print("=" * 60)

    try:
        import subprocess
        subprocess.Popen(["cmd", "/c", "start", "", url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        try:
            webbrowser.open(url)
        except Exception:
            print(f"请手动在浏览器打开：{url}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print("已退出。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
