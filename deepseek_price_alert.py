#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deepseek_price_alert.py — DeepSeek 官方 API 降价提醒工具
Monitor DeepSeek official API pricing and alert you when prices drop.

原理 / How it works:
  1. Fetch the official pricing page (api-docs.deepseek.com/quick_start/pricing)
  2. Parse model prices from the HTML table
  3. Compare with the last saved snapshot (price_history.json)
  4. If any price dropped -> show a desktop notification + append to log

零第三方依赖 / Zero third-party dependencies:
  Only Python standard library. Works on Windows / macOS / Linux.

用法 / Usage:
  python deepseek_price_alert.py --init     # 建立价格基线(首次运行)
  python deepseek_price_alert.py --once      # 单次检查并提醒
  python deepseek_price_alert.py --history  # 查看历史价格记录
  python deepseek_price_alert.py          # 默认: 同 --once

MIT License. 数据来源 / Data source: DeepSeek 官方定价页 (官方文档).
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# 常量配置 / Constants
# --------------------------------------------------------------------------
PRICING_URL = "https://api-docs.deepseek.com/quick_start/pricing"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
REQUEST_TIMEOUT = 30  # 秒

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "price_history.json"
LOG_FILE = BASE_DIR / "monitor.log"

# 价格下降多少才算"降价"(容差, 避免浮点误差误报) / Drop threshold
DROP_THRESHOLD = 0.999


# --------------------------------------------------------------------------
# 价格解析 / Price parsing
# --------------------------------------------------------------------------
def fetch_pricing_page() -> str:
    """抓取官方定价页 HTML / Fetch the official pricing page HTML."""
    req = urllib.request.Request(PRICING_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_prices(html: str) -> dict:
    """
    从 HTML 表格中解析价格, 返回:
    { "deepseek-flash": {"cache_hit_offpeak": 0.003, ..., "output_peak": 1.2},
      "deepseek-v4-pro": {...} }

    Parse model prices from the HTML tables.
    """
    tables = re.findall(r"<table.*?</table>", html, re.S | re.I)
    if not tables:
        raise ValueError("未在页面中找到价格表格 / No pricing table found")

    prices: dict = {}
    # 识别模型名: 表格中出现的 deepseek-* 模型标识
    model_aliases = {
        "deepseek-flash": "deepseek-flash",
        "deepseek-v4-pro": "deepseek-v4-pro",
    }

    # 从表格0(模型价格表)中提取
    for table in tables:
        text = re.sub(r"<[^>]+>", "|", table)
        text = re.sub(r"\|+", "|", text)
        cells = [c.strip() for c in text.split("|") if c.strip()]

        # 检查这个表里有哪些模型
        present_models = [m for m in model_aliases if m in text]
        if not present_models:
            continue  # 不是模型价格表(比如 Search & Fetch 表)

        # 提取所有美元价格及其前一个单元格(标签)
        dollar_prices = []
        for idx, cell in enumerate(cells):
            m = re.match(r"^\$([0-9]+(?:\.[0-9]+)?)$", cell)
            if m:
                label = cells[idx - 1] if idx > 0 else ""
                dollar_prices.append((label, float(m.group(1))))

        # 根据模型表结构分配价格。
        # 表格顺序(每列一个模型):
        #   1M INPUT TOKENS (CACHE HIT)   OFF-PEAK $a $b  / PEAK $c $d
        #   1M INPUT TOKENS (CACHE MISS)  OFF-PEAK $e $f  / PEAK $g $h
        #   1M OUTPUT TOKENS              OFF-PEAK $i $j  / PEAK $k $l
        # 其中 $a,$c,$e,$g,$i,$k 属于第一个模型, $b,$d,$f,$h,$j,$l 属于第二个模型。
        #
        # 我们从纯价格列表中按固定顺序取:
        # [cache_hit_off, cache_hit_off2, cache_hit_peak, cache_hit_peak2,
        #  cache_miss_off, cache_miss_off2, cache_miss_peak, cache_miss_peak2,
        #  output_off, output_off2, output_peak, output_peak2]
        vals = [v for _, v in dollar_prices if v > 0]
        # 去掉 0.75 (Search & Fetch 价格在同一页但不在模型表中 —— 不会混入,
        # 因为只在含模型名的表里收集)
        if len(vals) >= 12:
            m0, m1 = present_models[0], present_models[-1]
            prices[m0] = {
                "cache_hit_offpeak": vals[0],
                "cache_hit_peak": vals[2],
                "cache_miss_offpeak": vals[4],
                "cache_miss_peak": vals[6],
                "output_offpeak": vals[8],
                "output_peak": vals[10],
            }
            prices[m1] = {
                "cache_hit_offpeak": vals[1],
                "cache_hit_peak": vals[3],
                "cache_miss_offpeak": vals[5],
                "cache_miss_peak": vals[7],
                "output_offpeak": vals[9],
                "output_peak": vals[11],
            }
            break

    if not prices:
        raise ValueError("未能解析出模型价格 / Failed to parse model prices")
    return prices


# --------------------------------------------------------------------------
# 历史记录 / History persistence
# --------------------------------------------------------------------------
def load_history() -> dict:
    """读取历史价格快照."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_history(history: dict) -> None:
    """保存历史价格快照."""
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# --------------------------------------------------------------------------
# 提醒 / Notification
# --------------------------------------------------------------------------
def notify(title: str, message: str) -> None:
    """跨平台桌面通知 (Windows / macOS / Linux)."""
    system = sys.platform
    try:
        if system.startswith("win"):
            # Windows: PowerShell 弹窗 (无需第三方库)
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)
        elif system == "darwin":
            # macOS
            subprocess.run(
                ["osascript", "-e",
                 f'display notification "{message}" with title "{title}"'],
                check=True,
                timeout=15,
            )
        else:
            # Linux: 尝试 notify-send, 失败则打印
            subprocess.run(
                ["notify-send", title, message],
                check=True,
                timeout=15,
            )
    except Exception as exc:  # 通知失败不阻断主流程
        print(f"[通知失败/Notification failed] {exc}")


def log(msg: str) -> None:
    """写日志 (时间戳 + 消息)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# --------------------------------------------------------------------------
# 核心检查逻辑 / Core check logic
# --------------------------------------------------------------------------
def format_price(price: float) -> str:
    return f"${price:.4f}".rstrip("0").rstrip(".")


def compare_and_alert(current: dict, history: dict) -> bool:
    """
    对比当前价格与历史快照, 发现降价则提醒。
    返回: 是否有任何降价提醒触发。
    """
    # 首次运行(无历史) -> 建立基线, 不提醒
    if not history or "prices" not in history:
        log("首次运行: 建立价格基线 / First run: creating price baseline.")
        return False

    old_prices = history.get("prices", {})
    triggered = False
    dropped_lines = []

    for model, metrics in sorted(current.items()):
        old = old_prices.get(model)
        if not old:
            log(f"发现新模型 / New model detected: {model}")
            continue
        for metric, new_price in sorted(metrics.items()):
            old_price = old.get(metric)
            if old_price is None:
                continue
            if new_price < old_price * DROP_THRESHOLD:
                drop_pct = (1 - new_price / old_price) * 100
                line = (
                    f"📉 {model} {metric}: "
                    f"{format_price(old_price)} -> {format_price(new_price)} "
                    f"(-{drop_pct:.1f}%)"
                )
                dropped_lines.append(line)
                log(line)
                triggered = True
            elif new_price > old_price * (2 - DROP_THRESHOLD):
                # 涨价也记录一下 (只记录不弹窗)
                log(
                    f"📈 {model} {metric}: "
                    f"{format_price(old_price)} -> {format_price(new_price)}"
                )

    if dropped_lines:
        title = "DeepSeek API 降价提醒 🎉"
        message = "\n".join(dropped_lines)
        log(f"触发降价提醒 / Price drop alert triggered:\n{message}")
        notify(title, message)
    else:
        log("价格无下降变化 / No price drop detected.")

    return triggered


def run_check() -> int:
    """执行一次完整检查."""
    try:
        html = fetch_pricing_page()
        current = parse_prices(html)
    except Exception as exc:
        log(f"抓取/解析失败 / Fetch or parse failed: {exc}")
        return 1

    history = load_history()
    triggered = compare_and_alert(current, history)

    # 保存本次快照(总是更新)
    history["prices"] = current
    history["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(history)

    log("检查完成 / Check finished.")
    return 0 if triggered else 0


# --------------------------------------------------------------------------
# 历史查看 / History view
# --------------------------------------------------------------------------
def show_history() -> int:
    """打印历史价格记录."""
    history = load_history()
    if not history or "prices" not in history:
        print("还没有历史记录。先运行 --init 建立基线。")
        return 0

    print(f"最后检查时间 / Last checked: {history.get('last_checked', '?')}")
    print("-" * 60)
    for model, metrics in sorted(history["prices"].items()):
        print(f"\n{model}:")
        for metric, price in sorted(metrics.items()):
            print(f"  {metric:22s} {format_price(price)}")


# --------------------------------------------------------------------------
# 主入口 / Main
# --------------------------------------------------------------------------
def main() -> int:
    args = sys.argv[1:]

    if "--init" in args:
        html = fetch_pricing_page()
        current = parse_prices(html)
        history = load_history()
        history["prices"] = current
        history["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_history(history)
        log("基线已建立 / Baseline created.")
        for model, metrics in sorted(current.items()):
            log(f"  {model}: {json.dumps(metrics, ensure_ascii=False)}")
        return 0

    if "--history" in args:
        return show_history()

    # 默认: 单次检查
    return run_check()


if __name__ == "__main__":
    sys.exit(main())