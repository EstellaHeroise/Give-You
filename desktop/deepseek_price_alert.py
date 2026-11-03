#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.10.30
# =====================================================================
"""
deepseek_price_alert.py — DeepSeek 官方 API 降价提醒工具
Monitor DeepSeek official API pricing and alert you when prices drop.

原理 / How it works:
  1. Fetch the official pricing page (api-docs.deepseek.com/quick_start/pricing)
  2. Parse model prices from the HTML table
  3. Compare with the last saved snapshot (price_history.json)
  4. If any price dropped -> show a desktop notification + append to log
  5. Also watch official announcements (/updates) for promotions/price-cut news

零第三方依赖 / Zero third-party dependencies:
  Only Python standard library. Works on Windows / macOS / Linux.

用法 / Usage:
  python deepseek_price_alert.py --init     # 建立价格基线(首次运行)
  python deepseek_price_alert.py --once      # 单次检查并提醒
  python deepseek_price_alert.py --history  # 查看历史价格记录
  python deepseek_price_alert.py --check-update  # 手动检查是否有新版本
  python deepseek_price_alert.py          # 默认: 同 --once

原创使用许可 (Original Works License). 数据来源 / Data source: DeepSeek 官方定价页与官方公告 (官方文档).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# 常量配置 / Constants
# --------------------------------------------------------------------------
__version__ = "0.9.2"  # 当前版本，用于自动更新检测 / Current version

# GitHub 仓库地址（当前托管于作品集仓库 Give-You 的 tool-deepseek 分支）
# GitHub repo (the project lives in the Give-You repo, tool-deepseek branch)
GITHUB_REPO = "EstellaHeroise/Give-You"
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_DOWNLOAD_BASE = f"https://github.com/{GITHUB_REPO}/releases/latest/download"

PRICING_URL = "https://api-docs.deepseek.com/quick_start/pricing"
UPDATES_URL = "https://api-docs.deepseek.com/updates"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
REQUEST_TIMEOUT = 30  # 秒

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "price_history.json"
LOG_FILE = BASE_DIR / "monitor.log"
CONFIG_FILE = BASE_DIR / "config.json"

# 价格下降多少才算"降价"(容差, 避免浮点误差误报) / Drop threshold
DROP_THRESHOLD = 0.999

# 默认汇率(USD -> CNY), 可通过环境变量 DEEPSEEK_ALERT_USD_CNY 覆盖
# Default exchange rate, override with env var DEEPSEEK_ALERT_USD_CNY
import os
DEFAULT_USD_CNY = float(os.environ.get("DEEPSEEK_ALERT_USD_CNY", "7.1"))

# 大额优惠判定 / "Big deal" thresholds:
#   - 降幅 >= 50%
#   - 或折算后 <= 0.01 元/万token (即"一分钱一万token"级别)
BIG_DROP_PCT = 50.0
PENNY_PER_10K_CNY = 0.01  # 元/万token

# 公告关键词: 命中说明与降价/优惠相关
PROMO_KEYWORDS = (
    "降价", "优惠", "折扣", "限时", "免费", "价格调整", "price", "discount",
    "promotion", "off-peak", "错峰", "下调", "降幅", "活动", "deal", "sale",
)


# --------------------------------------------------------------------------
# 工具函数 / Utilities
# --------------------------------------------------------------------------
def http_get(url: str) -> str:
    """抓取网页内容 / Fetch a URL and return decoded HTML."""
    # 显式禁用代理：避免环境变量 HTTP_PROXY/HTTPS_PROXY 干扰请求
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def format_usd(price: float) -> str:
    """$ per 1M tokens -> 去掉多余尾零."""
    return f"${price:.4f}".rstrip("0").rstrip(".")


def to_cny_per_10k(usd_per_1m: float, rate: float) -> float:
    """
    把 $/百万token 换算成 元/万token。
    usd_per_1m: 每百万token的美元价
    1M tokens = 100 万token = 100 * 1万token
    => 每万token = usd_per_1m / 100 * rate (元)
    """
    return usd_per_1m / 100.0 * rate


def format_cny_per_10k(cny_per_10k: float) -> str:
    """元/万token, 保留4位(能显示 0.01 一分钱)."""
    return f"¥{cny_per_10k:.4f}/万token"


def format_price_for_display(price: float, unit: str, rate: float) -> str:
    """
    按用户选择的单位格式化价格。
    unit: auto / usd_per_1m / cny_per_10k / cny_per_1m
    """
    if unit == "usd_per_1m":
        return f"{format_usd(price)}/1M"
    elif unit == "cny_per_1m":
        return f"¥{price * rate:.4f}/百万token"
    elif unit == "cny_per_10k":
        return f"¥{price / 100.0 * rate:.4f}/万token"
    else:  # auto: 同时显示两种
        cny_per_10k = to_cny_per_10k(price, rate)
        return f"{format_usd(price)}/1M = {format_cny_per_10k(cny_per_10k)}"


def is_penny_deal(cny_per_10k: float) -> bool:
    """是否达到"一分钱一万token"级别."""
    return cny_per_10k <= PENNY_PER_10K_CNY


def log(msg: str) -> None:
    """写日志 (时间戳 + 消息), 并按终端风格格式化."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    style = get_terminal_style()

    if style == "compact":
        line = msg
    elif style == "table":
        line = f"| {ts} | {msg}"
    else:  # log / color 都用 [时间] 消息
        line = f"[{ts}] {msg}"

    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def notify(title: str, message: str) -> None:
    """跨平台桌面通知 (Windows / macOS / Linux).

    根据 config.json 的 reminder_channel 决定是否播放系统提示音:
      - popup: 仅弹窗
      - popup_sound: 弹窗 + 系统提示音
    """
    system = sys.platform
    channel = get_reminder_channel()
    play_sound = channel == "popup_sound"

    try:
        if system.startswith("win"):
            import ctypes
            if play_sound:
                # 播放系统提示音 (MB_ICONASTERISK 自带提示音)
                ctypes.windll.user32.MessageBeep(0x40)
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)
        elif system == "darwin":
            if play_sound:
                subprocess.run(
                    ["osascript", "-e", "beep"],
                    check=True, timeout=10,
                )
            subprocess.run(
                ["osascript", "-e",
                 f'display notification "{message}" with title "{title}"'],
                check=True, timeout=15,
            )
        else:
            if play_sound:
                print("\a")  # 终端响铃
            subprocess.run(
                ["notify-send", title, message],
                check=True, timeout=15,
            )
    except Exception as exc:
        print(f"[通知失败/Notification failed] {exc}")


# --------------------------------------------------------------------------
# 价格解析 / Price parsing
# --------------------------------------------------------------------------
def parse_prices(html: str) -> dict:
    """
    从 HTML 表格中解析价格, 返回:
    { "deepseek-flash": {"cache_hit_offpeak": 0.003, ..., "output_peak": 1.2},
      "deepseek-v4-pro": {...} }
    """
    tables = re.findall(r"<table.*?</table>", html, re.S | re.I)
    if not tables:
        raise ValueError("未在页面中找到价格表格 / No pricing table found")

    prices: dict = {}
    model_aliases = {
        "deepseek-flash": "deepseek-flash",
        "deepseek-v4-pro": "deepseek-v4-pro",
    }

    for table in tables:
        text = re.sub(r"<[^>]+>", "|", table)
        text = re.sub(r"\|+", "|", text)
        cells = [c.strip() for c in text.split("|") if c.strip()]

        present_models = [m for m in model_aliases if m in text]
        if not present_models:
            continue

        dollar_prices = []
        for idx, cell in enumerate(cells):
            m = re.match(r"^\$([0-9]+(?:\.[0-9]+)?)$", cell)
            if m:
                dollar_prices.append(float(m.group(1)))

        vals = [v for v in dollar_prices if v > 0]
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
# 公告解析 / Announcements parsing
# --------------------------------------------------------------------------
def parse_updates(html: str) -> list:
    """
    从 /updates 页面解析公告列表, 返回:
    [{"title": "DeepSeek-V4.1-Flash-1017 Release", "url": "...", "date": "...?}]
    """
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)

    items = []
    seen = set()
    # 匹配 <a href="...news...">label</a>
    for href, label in re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', text, re.S):
        label = re.sub(r"<[^>]+>", "", label).strip()
        if "news" not in href or not label or href in seen:
            continue
        seen.add(href)
        # 标题里可能带日期, 如 "DeepSeek-R1 Release"
        items.append({"title": label, "url": href})

    return items


def announcement_matches_promo(title: str) -> bool:
    """判断公告标题是否与降价/优惠相关."""
    lower = title.lower()
    return any(kw.lower() in lower for kw in PROMO_KEYWORDS)


# --------------------------------------------------------------------------
# 自动更新检测 / Auto update check
# --------------------------------------------------------------------------
def check_for_update(silent: bool = False) -> None:
    """
    检查 GitHub 上是否有新版本。
    若有新版，打印提示（不自动下载，保持零依赖与安全）。
    silent=True 时不打印"没有更新"这类无变化信息（用于定时/开机等静默场景）。
    """
    if "<YOUR_GITHUB_USERNAME>" in GITHUB_REPO:
        return  # 尚未配置真实仓库地址，跳过

    try:
        html = http_get(GITHUB_RELEASES_API)
        data = json.loads(html)
        latest = str(data.get("tag_name", "")).lstrip("vV")
        if not latest:
            return
    except Exception as exc:
        log(f"检查更新失败 / Update check failed: {exc}")
        return

    current = __version__.lstrip("vV")
    if latest == current:
        if not silent:
            log(f"已是最新版本 / Already up to date: v{current}")
        return

    log(
        f"发现新版本 / New version available: v{latest} (当前 v{current})\n"
        f"  下载 / Download: {GITHUB_DOWNLOAD_BASE}/deepseek-price-alert-setup-{latest}.zip\n"
        f"  或前往 Releases 页 / Or visit: https://github.com/{GITHUB_REPO}/releases"
    )


# --------------------------------------------------------------------------
# 历史记录 / History persistence
# --------------------------------------------------------------------------
def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# --------------------------------------------------------------------------
# 配置读写 / Config I/O (风格选择器 style_picker.html 保存的配置)
# --------------------------------------------------------------------------
def load_config() -> dict:
    """读取 config.json, 不存在时返回默认值."""
    defaults = {
        "notification_style": "clean",
        "terminal_style": "log",
        "window_theme": "light",
        "price_unit": "auto",
        "reminder_channel": "popup",  # popup 仅弹窗 / popup_sound 弹窗+声音
    }
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            for k, v in defaults.items():
                cfg.setdefault(k, v)
            return cfg
        except (json.JSONDecodeError, OSError):
            pass
    return defaults


def get_terminal_style() -> str:
    """返回终端输出风格 key."""
    return load_config().get("terminal_style", "log")


def get_price_unit() -> str:
    """返回价格显示单位: auto / usd_per_1m / cny_per_10k / cny_per_1m."""
    return load_config().get("price_unit", "auto")


def get_reminder_channel() -> str:
    """返回提醒方式: popup 仅弹窗 / popup_sound 弹窗+声音."""
    return load_config().get("reminder_channel", "popup")


# --------------------------------------------------------------------------
# 核心检查逻辑 / Core check logic
# --------------------------------------------------------------------------
def build_price_lines(current: dict, old_prices: dict, rate: float):
    """
    对比当前与历史价格, 生成提醒行。
    返回 (lines, has_drop, has_big_deal)
      lines: 每行包含模型/指标/新旧价格/按配置单位的显示/降幅/重点标记
    """
    lines = []
    has_drop = False
    has_big_deal = False
    unit = get_price_unit()

    for model, metrics in sorted(current.items()):
        old = old_prices.get(model)
        if not old:
            log(f"发现新模型 / New model detected: {model}")
            continue
        for metric, new_price in sorted(metrics.items()):
            old_price = old.get(metric)
            if old_price is None:
                continue

            # 涨价只记录, 不提醒
            if new_price > old_price * (2 - DROP_THRESHOLD):
                log(
                    f"📈 {model} {metric}: "
                    f"{format_price_for_display(old_price, unit, rate)} -> "
                    f"{format_price_for_display(new_price, unit, rate)}"
                )
                continue

            # 降价
            if new_price < old_price * DROP_THRESHOLD:
                drop_pct = (1 - new_price / old_price) * 100
                cny_per_10k = to_cny_per_10k(new_price, rate)
                big = drop_pct >= BIG_DROP_PCT or is_penny_deal(cny_per_10k)
                mark = "🔥 " if big else "📉 "
                line = (
                    f"{mark}{model} {metric}: "
                    f"{format_price_for_display(old_price, unit, rate)} -> "
                    f"{format_price_for_display(new_price, unit, rate)} "
                    f"(-{drop_pct:.1f}%)"
                )
                lines.append(line)
                log(line)
                has_drop = True
                if big:
                    has_big_deal = True

    return lines, has_drop, has_big_deal


def compare_and_alert(current: dict, history: dict, rate: float) -> bool:
    """对比价格并提醒, 返回是否有降价."""
    if not history or "prices" not in history:
        log("首次运行: 建立价格基线 / First run: creating price baseline.")
        return False

    old_prices = history.get("prices", {})
    lines, has_drop, has_big_deal = build_price_lines(current, old_prices, rate)

    if lines:
        title = "🔥 DeepSeek 大额降价!" if has_big_deal else "DeepSeek API 降价提醒 🎉"
        message = "\n".join(lines)
        log(f"触发降价提醒 / Price drop alert triggered:\n{message}")
        notify(title, message)
    else:
        log("价格无下降变化 / No price drop detected.")

    return has_drop


def check_updates(history: dict, rate: float) -> None:
    """
    检查官方公告列表, 发现新的且与降价/优惠相关的公告则提醒。
    """
    try:
        html = http_get(UPDATES_URL)
        items = parse_updates(html)
    except Exception as exc:
        log(f"公告抓取失败 / Updates fetch failed: {exc}")
        return

    if not items:
        return

    seen = history.get("seen_updates", [])
    seen_set = set(seen)

    new_promo = []
    for item in items:
        if item["url"] in seen_set:
            continue
        # 记录已见(无论是否优惠)
        seen.append(item["url"])
        if announcement_matches_promo(item["title"]):
            new_promo.append(item)

    history["seen_updates"] = seen[-100:]  # 只保留最近100条

    if new_promo:
        lines = []
        for it in new_promo:
            line = f"📢 官方公告: {it['title']} ({it['url']})"
            lines.append(line)
            log(line)
        title = "DeepSeek 官方优惠公告 🔥"
        message = "\n".join(lines)
        notify(title, message)


# --------------------------------------------------------------------------
# 运行入口 / Entry points
# --------------------------------------------------------------------------
def run_check() -> int:
    """执行一次完整检查."""
    rate = DEFAULT_USD_CNY
    try:
        html = http_get(PRICING_URL)
        current = parse_prices(html)
    except Exception as exc:
        log(f"抓取/解析价格失败 / Fetch or parse failed: {exc}")
        return 1

    history = load_history()
    compare_and_alert(current, history, rate)

    # 检查公告
    check_updates(history, rate)

    # 检查是否有新版本（静默模式：有更新才提示，无更新不打扰）
    check_for_update(silent=True)

    # 保存本次快照(总是更新)
    history["prices"] = current
    history["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(history)

    log("检查完成 / Check finished.")
    return 0


def show_history() -> int:
    """打印历史价格记录."""
    history = load_history()
    if not history or "prices" not in history:
        print("还没有历史记录。先运行 --init 建立基线。")
        return 0

    cfg = load_config()
    unit = cfg.get("price_unit", "auto")
    print(f"最后检查时间 / Last checked: {history.get('last_checked', '?')}")
    print(f"汇率 / Rate: 1 USD = {DEFAULT_USD_CNY} CNY")
    print(f"当前风格 / Style: 通知={cfg.get('notification_style')}, "
          f"终端={cfg.get('terminal_style')}, 主题={cfg.get('window_theme')}, "
          f"单位={unit}")
    print("-" * 72)
    for model, metrics in sorted(history["prices"].items()):
        print(f"\n{model}:")
        for metric, price in sorted(metrics.items()):
            display = format_price_for_display(price, unit, DEFAULT_USD_CNY)
            print(f"  {metric:22s} {display}")

    seen = history.get("seen_updates", [])
    if seen:
        print(f"\n已见公告数 / Seen updates: {len(seen)}")
    return 0


def resolve_python_exe() -> Path:
    """返回写进开机自启 / 定时任务里的 Python 路径。

    优先用脚本同目录下的内置 Python（安装后的稳定位置）。
    不能直接用 sys.executable：从安装包解压目录启动安装时，它指向那个临时目录，
    用户一删安装包，开机自启和定时任务就会静默失效（0.9.1 及以前的 bug）。
    """
    bundled = BASE_DIR / "python" / "python.exe"
    return bundled if bundled.exists() else Path(sys.executable)


def get_startup_script_path() -> Path:
    """返回 Windows 启动文件夹里的启动脚本路径."""
    # 用用户启动文件夹 (shell:startup)
    startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return startup_dir / "deepseek_price_alert.vbs"


def get_scheduler_task_name() -> str:
    """返回计划任务名称."""
    return "DeepSeekPriceAlertDaily"


def setup_startup() -> int:
    """
    设置开机自启: 在 Windows 启动文件夹创建 VBS 脚本,
    开机后静默运行 python deepseek_price_alert.py --once (自动检查价格)。
    """
    if not sys.platform.startswith("win"):
        print("开机自启目前仅支持 Windows / Startup is only supported on Windows.")
        return 1

    script_path = get_startup_script_path()
    python_exe = resolve_python_exe()
    script = rf'''Set ws = CreateObject("Wscript.Shell")
ws.Run """"{python_exe}"" ""{BASE_DIR / 'deepseek_price_alert.py'}"" --once", 0, False
'''

    try:
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script, encoding="utf-8")
        print(f"✅ 开机自启已设置 / Startup enabled: {script_path}")
        print("   (开机后会自动检查一次 DeepSeek 价格，有降价才提醒)")
        return 0
    except OSError as exc:
        print(f"❌ 设置开机自启失败 / Failed to enable startup: {exc}")
        return 1


def remove_startup() -> int:
    """取消开机自启."""
    if not sys.platform.startswith("win"):
        print("开机自启目前仅支持 Windows / Startup is only supported on Windows.")
        return 1

    script_path = get_startup_script_path()
    try:
        if script_path.exists():
            script_path.unlink()
            print(f"✅ 已取消开机自启 / Startup disabled: {script_path}")
        else:
            print("ℹ️ 尚未设置开机自启 / No startup script found.")
        return 0
    except OSError as exc:
        print(f"❌ 取消开机自启失败 / Failed to disable startup: {exc}")
        return 1


def setup_schedule(time_str: str) -> int:
    """
    设置每日定时提醒: 通过 schtasks 创建每天固定时间运行 --once 的任务。
    time_str 格式: HH:MM (24小时制, 如 09:30)。
    """
    if not sys.platform.startswith("win"):
        print("定时提醒目前仅支持 Windows / Schedule is only supported on Windows.")
        return 1

    # 校验时间格式
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        print("❌ 时间格式错误，请用 24 小时制 HH:MM，例如 09:30")
        return 1

    task_name = get_scheduler_task_name()
    python_exe = resolve_python_exe()
    script = str(BASE_DIR / "deepseek_price_alert.py")

    # 构建 schtasks 命令
    cmd = [
        "schtasks", "/Create", "/TN", task_name,
        "/TR", f'"{python_exe}" "{script}" --once',
        "/SC", "DAILY", "/ST", time_str,
        "/F",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            print(f"✅ 每日定时提醒已设置 / Daily reminder set: {time_str}")
            print("   (每天到点会自动检查 DeepSeek 价格，有降价才提醒)")
            return 0
        else:
            print(f"❌ 设置定时提醒失败 / Failed to set schedule: {result.stderr.strip()}")
            return 1
    except OSError as exc:
        print(f"❌ 设置定时提醒失败 / Failed to set schedule: {exc}")
        return 1


def remove_schedule() -> int:
    """取消每日定时提醒."""
    if not sys.platform.startswith("win"):
        print("定时提醒目前仅支持 Windows / Schedule is only supported on Windows.")
        return 1

    task_name = get_scheduler_task_name()
    cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            print("✅ 已取消每日定时提醒 / Daily reminder disabled.")
        else:
            # 区分"任务不存在"和其他错误
            err = result.stderr.strip()
            if "not found" in err.lower() or "不存在" in err:
                print("ℹ️ 尚未设置定时提醒 / No scheduled task found.")
            else:
                print(f"❌ 取消定时提醒失败 / Failed to remove schedule: {err}")
        return 0
    except OSError as exc:
        print(f"❌ 取消定时提醒失败 / Failed to remove schedule: {exc}")
        return 1


def show_status() -> int:
    """查看开机自启和定时提醒状态 (不依赖 schtasks 外部命令)."""
    print("=== 提醒功能状态 / Reminder status ===\n")

    if not sys.platform.startswith("win"):
        print("当前平台非 Windows，开机自启和定时提醒暂不支持。")
        return 0

    # 开机自启: 检查启动文件夹脚本是否存在
    startup_path = get_startup_script_path()
    if startup_path.exists():
        print(f"✅ 开机自启: 已启用 / Startup: enabled")
        print(f"   脚本: {startup_path}")
    else:
        print(f"❌ 开机自启: 未启用 / Startup: disabled")
    print()

    # 定时任务: 通过注册表 TaskCache 检查任务是否存在 (避免调用 schtasks)
    task_name = get_scheduler_task_name()
    task_reg_path = (
        r"Software\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache"
    )
    task_exists = False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, task_reg_path) as key:
            # 树状结构: TaskCache\Tree\<任务名>
            try:
                with winreg.OpenKey(key, r"Tree\\" + task_name):
                    task_exists = True
            except FileNotFoundError:
                task_exists = False
    except Exception:
        # 无法读取注册表时，退化为"未设置"
        task_exists = False

    if task_exists:
        print(f"✅ 每日定时提醒: 已设置 / Daily reminder: enabled")
    else:
        print(f"❌ 每日定时提醒: 未设置 / Daily reminder: disabled")

    print(f"\n提醒方式 / Channel: {get_reminder_channel()}"
          f"({'仅弹窗' if get_reminder_channel() == 'popup' else '弹窗+声音'})")
    return 0


def main() -> int:
    args = sys.argv[1:]

    # 显示版本 / Show version
    if "--version" in args or "-v" in args:
        print(f"deepseek-price-alert v{__version__}")
        return 0

    # 显示帮助 / Show help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # 开机自启 / Startup
    if "--setup-startup" in args:
        return setup_startup()
    if "--remove-startup" in args:
        return remove_startup()

    # 每日定时提醒 / Daily schedule
    if "--setup-schedule" in args:
        # 用法: --setup-schedule HH:MM
        idx = args.index("--setup-schedule")
        if idx + 1 < len(args):
            return setup_schedule(args[idx + 1])
        print("用法 / Usage: python deepseek_price_alert.py --setup-schedule HH:MM")
        print("示例 / Example: python deepseek_price_alert.py --setup-schedule 09:30")
        return 1
    if "--remove-schedule" in args:
        return remove_schedule()

    # 查看提醒状态 / Status
    if "--status" in args:
        return show_status()

    # 手动检查更新 / Check for updates manually
    if "--check-update" in args:
        check_for_update(silent=False)
        return 0

    # 建立价格基线 / Create baseline
    if "--init" in args:
        html = http_get(PRICING_URL)
        current = parse_prices(html)
        history = load_history()
        history["prices"] = current
        history["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_history(history)
        log("基线已建立 / Baseline created.")
        for model, metrics in sorted(current.items()):
            log(f"  {model}: {json.dumps(metrics, ensure_ascii=False)}")
        return 0

    # 查看历史 / View history
    if "--history" in args:
        return show_history()

    # 默认: 单次检查 / Default: one-time check
    return run_check()


if __name__ == "__main__":
    sys.exit(main())