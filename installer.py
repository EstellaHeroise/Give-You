#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.10.30
# =====================================================================
"""
installer.py — DeepSeek 降价提醒工具 二合一安装向导
=====================================================
一个安装包同时包含「桌面通用版」与「WorkBuddy 适配版」，
用户双击安装包后在图形页面中选择要安装的版本，一键完成安装。

设计 / Design:
  - 零第三方依赖（仅 Python 标准库）
  - 用内置 http.server 启动本地网页安装向导，自动打开浏览器
  - 前端 installer.html 展示两个版本卡片，用户选择后 POST 回本服务
  - 后端按选择执行安装：复制文件、可选配置开机自启等
  - v0.9.3 起：风格选择（终端输出 / 价格单位 / 提醒方式）合并进安装向导，
    安装时直接写入 config.json，用户不必再单独打开 style_picker.html 搬文件

用法 / Usage:
  python installer.py            # 启动安装向导（默认端口 8765）
  python installer.py --port 9000
  python installer.py --test     # 自检模式：不打开浏览器，仅启动服务供测试

原创使用许可 (Original Works License).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# --------------------------------------------------------------------------
# 路径与常量 / Paths & constants
# --------------------------------------------------------------------------
INSTALLER_DIR = Path(__file__).resolve().parent
VERSION = "0.9.3"

# GitHub 仓库地址（当前托管于作品集仓库 Give-You 的 tool-deepseek 分支）
GITHUB_REPO = "EstellaHeroise/Give-You"
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# 安装目标根目录（默认在用户主目录下，两版本子目录分离，互不冲突）
DEFAULT_TARGET_ROOT = Path("D:\\deepseek-price-alert")

# 两个版本的目标子目录
DESKTOP_SUBDIR = "desktop"
WORKBUDDY_SUBDIR = "workbuddy"

# 源文件目录（安装包内的目录）
SOURCE_DESKTOP = INSTALLER_DIR / "desktop"
SOURCE_WORKBUDDY = INSTALLER_DIR / "workbuddy"
SOURCE_PYTHON = INSTALLER_DIR / "python"  # 内置便携 Python（无需用户自行安装）

# WorkBuddy skills 目录（用户级）
WORKBUDDY_SKILLS_DIR = Path.home() / ".workbuddy" / "skills" / "deepseek-price-alert"

# 安装日志（写入系统临时目录，便于排查）
LOG_PATH = Path(tempfile.gettempdir()) / "deepseek_installer.log"

# 页面文件
PAGE_FILE = INSTALLER_DIR / "installer.html"

# 安装包 ZIP 路径的环境变量名（install.bat 启动时设置，供安装后自动删除）
SETUP_ZIP_ENV = "DEEPSEEK_ALERT_SETUP_ZIP"


# --------------------------------------------------------------------------
# 日志 / Logging
# --------------------------------------------------------------------------
def log(msg: str) -> None:
    ts_line = f"[installer] {msg}"
    print(ts_line)
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(ts_line + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------
# 自动更新检测 / Auto update check
# --------------------------------------------------------------------------
def check_for_update() -> None:
    """检查 GitHub 上是否有比当前安装包更新的版本，有则打印提示。"""
    if "<YOUR_GITHUB_USERNAME>" in GITHUB_REPO:
        return  # 尚未配置真实仓库地址，跳过

    try:
        import urllib.request
        # 显式禁用代理：避免环境变量 HTTP_PROXY/HTTPS_PROXY 干扰本地服务
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(
            GITHUB_RELEASES_API,
            headers={"User-Agent": "Mozilla/5.0 deepseek-price-alert-installer"},
        )
        with opener.open(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        latest = str(data.get("tag_name", "")).lstrip("vV")
        if not latest:
            return
    except Exception as exc:
        # 404 = 仓库还没有 Releases（本项目用分支里的 zip 分发），不算错误，静默跳过
        is_404 = getattr(exc, "code", None) == 404 or "404" in str(exc)
        if not is_404:
            log(f"检查更新失败（不影响安装） / Update check failed: {exc}")
        return

    if latest != VERSION.lstrip("vV"):
        log(
            f"发现新版本 / New version available: v{latest} (当前安装包 v{VERSION})\n"
            f"  请前往 GitHub Releases 下载最新安装包: "
            f"https://github.com/{GITHUB_REPO}/releases"
        )
    else:
        log(f"已是最新版本 / Already up to date: v{VERSION}")


# --------------------------------------------------------------------------
# 文件复制辅助 / File copy helpers
# --------------------------------------------------------------------------
def copy_tree(src: Path, dst: Path) -> None:
    """复制整个目录树，目标已存在时先覆盖."""
    if not src.exists():
        raise FileNotFoundError(f"源目录不存在: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = item
        d = dst / item.name
        if item.is_dir():
            copy_tree(item, d)
        else:
            shutil.copy2(s, d)
            log(f"复制 / Copied: {d}")


def ensure_python() -> str:
    """返回可用的 python 解释器路径."""
    return sys.executable


def deploy_runtime(target_dir: Path) -> None:
    """
    把内置便携 Python 与启动器(run.bat)一起部署到安装目录。

    这样用户无需自行安装 Python：双击 run.bat 即可运行工具；
    且开机自启 / 定时任务基于 sys.executable，会自动指向内置 Python。
    """
    if not SOURCE_PYTHON.exists():
        log(f"[warn] 未找到内置 Python（{SOURCE_PYTHON}），跳过运行时部署。")
        return
    dest_py = target_dir / "python"
    copy_tree(SOURCE_PYTHON, dest_py)
    run_bat = target_dir / "run.bat"
    run_bat.write_text(
        "@echo off\n"
        "cd /d \"%~dp0\"\n"
        "if not exist \"python\\python.exe\" (\n"
        "  echo [错误] 未找到内置 Python（python\\python.exe），请重新安装本工具。\n"
        "  pause\n"
        "  exit /b 1\n"
        ")\n"
        "\"python\\python.exe\" deepseek_price_alert.py %*\n",
        encoding="utf-8",
    )
    log(f"已部署内置运行时 / Deployed bundled runtime: {dest_py}")


def cleanup_installer(remove_zip: bool = True) -> dict:
    """
    安装完成后自动清理安装包：
    - 删除当前解压目录（即 INSTALLER_DIR 本身，包含 installer.py/html/desktop/skill 等）
    - 删除原 ZIP 安装包（优先使用 install.bat 通过环境变量 DEEPSEEK_ALERT_SETUP_ZIP 传入的路径，
      否则回退为查找解压目录上一级的 deepseek-price-alert-setup-*.zip）。
    注意：此函数应在安装逻辑成功完成后调用。
    """
    cleaned = {"unpacked_dir": None, "zip": None}

    # 1. 记录并删除解压目录（安装包的"临时家"）
    try:
        unpacked = INSTALLER_DIR
        if unpacked.exists():
            # 保护：不要误删用户主目录 / 项目源码目录
            # 仅当目录名是 "deepseek-price-alert-setup-*" 或包含 installer.py 时才清理
            is_setup_dir = (
                unpacked.name.startswith("deepseek-price-alert-setup-")
                or (unpacked / "installer.py").exists()
            )
            home = Path.home().resolve()
            if is_setup_dir and unpacked.resolve() != home and unpacked.resolve() != Path.cwd().resolve():
                shutil.rmtree(unpacked, ignore_errors=True)
                cleaned["unpacked_dir"] = str(unpacked)
                log(f"已删除解压目录 / Removed unpacked dir: {unpacked}")
    except Exception as exc:
        log(f"清理解压目录失败 / Failed to remove unpacked dir: {exc}")

    # 2. 删除原 ZIP 安装包
    if remove_zip:
        try:
            # 优先使用环境变量指定的 ZIP 路径（install.bat 传入）
            env_zip = os.environ.get(SETUP_ZIP_ENV, "").strip()
            if env_zip:
                z = Path(env_zip).expanduser().resolve()
                if z.exists() and z.suffix.lower() == ".zip":
                    try:
                        z.unlink()
                        cleaned["zip"] = str(z)
                        log(f"已删除安装包 / Removed installer zip: {z}")
                    except OSError as exc:
                        log(f"删除安装包失败 / Failed to remove zip {z}: {exc}")
            # 回退：查找解压目录上一级的 zip
            if not cleaned["zip"]:
                parent = INSTALLER_DIR.parent
                for z in sorted(parent.glob("deepseek-price-alert-setup-*.zip")):
                    try:
                        z.unlink()
                        cleaned["zip"] = str(z)
                        log(f"已删除安装包 / Removed installer zip: {z}")
                    except OSError as exc:
                        log(f"删除安装包失败 / Failed to remove zip {z}: {exc}")
        except Exception as exc:
            log(f"清理安装包失败 / Failed to clean zip: {exc}")

    return cleaned


# --------------------------------------------------------------------------
# 风格配置 / Style config  (v0.9.3：风格选择已合并进安装向导)
# --------------------------------------------------------------------------
# 与 deepseek_price_alert.py 的 load_config() 默认值严格保持一致
STYLE_DEFAULTS = {
    "notification_style": "clean",
    "terminal_style": "log",
    "window_theme": "light",
    "price_unit": "auto",
    "reminder_channel": "popup",
}

# 只有主脚本真正读取并生效的项才允许在安装向导里选择；
# notification_style / window_theme 目前仅被预览页使用，主脚本未读取，
# 因此不列入可选白名单，避免用户选了却不生效。
STYLE_CHOICES = {
    "terminal_style": {"log", "table", "compact", "color"},
    "price_unit": {"auto", "usd_per_1m", "cny_per_10k", "cny_per_1m"},
    "reminder_channel": {"popup", "popup_sound"},
}


def normalize_style(style):
    """
    校验前端提交的风格配置。只保留白名单内的合法值，非法值直接丢弃（不报错，
    避免因为一个错值导致整个安装失败）。一个合法值都没有时返回 None。
    """
    if not isinstance(style, dict):
        return None
    picked = {}
    for key, allowed in STYLE_CHOICES.items():
        val = style.get(key)
        if isinstance(val, str) and val in allowed:
            picked[key] = val
    return picked or None


def write_config(target_dir, style):
    """
    把风格写入 <target_dir>/config.json。

    - style 为 None（用户没动风格区）：config.json 已存在就原样保留，
      不存在才写默认值 —— 保证重装不会把用户已调好的风格冲掉。
    - style 为 dict：只覆盖它包含的那几项，其余字段保留用户已有值。

    返回写入的路径；跳过或失败时返回 None。
    """
    if target_dir is None:
        return None
    cfg_file = Path(target_dir) / "config.json"
    incoming = normalize_style(style)

    existing = {}
    if cfg_file.exists():
        try:
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                existing = data
        except (json.JSONDecodeError, OSError):
            existing = {}

    if incoming is None:
        if existing:
            log(f"保留已有风格配置 / Keep existing config: {cfg_file}")
            return cfg_file
        cfg = dict(STYLE_DEFAULTS)
    else:
        cfg = {**STYLE_DEFAULTS, **existing, **incoming}

    try:
        cfg_file.parent.mkdir(parents=True, exist_ok=True)
        cfg_file.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        log(f"已写入风格配置 / Wrote config: {cfg_file} -> {cfg}")
        return cfg_file
    except OSError as exc:
        log(f"写入风格配置失败 / Failed to write config: {exc}")
        return None


# --------------------------------------------------------------------------
# 安装逻辑 / Install logic
# --------------------------------------------------------------------------
def install_desktop(target_root: Path, enable_startup: bool, style=None) -> dict:
    """
    安装桌面通用版。
    1. 复制 desktop/ 下的文件到 <target_root>/desktop
    2. 可选：配置开机自启（调用主脚本 --setup-startup）
    """
    target_dir = target_root / DESKTOP_SUBDIR
    target_dir.mkdir(parents=True, exist_ok=True)

    copy_tree(SOURCE_DESKTOP, target_dir)
    deploy_runtime(target_dir)
    # 卸载脚本放到安装根目录，之后双击它即可清理干净
    uninstall_src = INSTALLER_DIR / "uninstall.bat"
    if uninstall_src.exists():
        shutil.copy2(uninstall_src, target_root / "uninstall.bat")

    results = {
        "version": "桌面通用版 / Desktop Edition",
        "install_dir": str(target_dir),
        "startup": False,
        "files": [],
        "configs": [],
    }

    # 风格配置：装完就是配好的（v0.9.3 起合并进安装向导）
    cfg_path = write_config(target_dir, style)
    if cfg_path:
        results["configs"].append(str(cfg_path))

    # 记录已安装文件（便于卸载/查看）
    for item in sorted(target_dir.rglob("*")):
        if item.is_file():
            results["files"].append(str(item))

    if enable_startup:
        python_exe = ensure_python()
        script = target_dir / "deepseek_price_alert.py"
        cmd = [python_exe, str(script), "--setup-startup"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=30)
            results["startup"] = r.returncode == 0
            if r.stdout:
                log(f"开机自启输出 / Startup output: {r.stdout.strip()}")
            if r.stderr:
                log(f"开机自启 stderr / Startup stderr: {r.stderr.strip()}")
        except Exception as exc:
            log(f"配置开机自启失败 / Startup setup failed: {exc}")
            results["startup"] = False

    return results


def install_workbuddy(target_root: Path, also_desktop: bool,
                      enable_startup: bool, style=None) -> dict:
    """
    安装 WorkBuddy 适配版。
    1. 复制 skill/ 到 WorkBuddy 用户级 skills 目录（~/.workbuddy/skills/deepseek-price-alert）
    2. 把风格写入该 skill 目录的 config.json（v0.9.3 起）
    3. 若 also_desktop 为真，同时把桌面版程序复制到 <target_root>/desktop（联动版）
    4. 可选：配置开机自启
    """
    results = {
        "version": "WorkBuddy 适配版 / WorkBuddy Edition",
        "skill_dir": str(WORKBUDDY_SKILLS_DIR),
        "desktop_dir": None,
        "startup": False,
        "files": [],
        "configs": [],
    }

    # 1. 复制 skill
    try:
        WORKBUDDY_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        # 复制 SKILL.md 与脚本（skill 目录内容）
        for item in (INSTALLER_DIR / "skill").iterdir():
            d = WORKBUDDY_SKILLS_DIR / item.name
            if item.is_dir():
                copy_tree(item, d)
            else:
                shutil.copy2(item, d)
                log(f"复制 / Copied: {d}")
                results["files"].append(str(d))
    except Exception as exc:
        raise RuntimeError(f"安装 WorkBuddy skill 失败: {exc}") from exc

    # 2. 风格配置写进 skill 目录（WorkBuddy 版从这里读）
    cfg_skill = write_config(WORKBUDDY_SKILLS_DIR, style)
    if cfg_skill:
        results["configs"].append(str(cfg_skill))

    # 3. 可选：同时安装桌面联动版
    if also_desktop:
        target_dir = target_root / DESKTOP_SUBDIR
        target_dir.mkdir(parents=True, exist_ok=True)
        copy_tree(SOURCE_DESKTOP, target_dir)
        deploy_runtime(target_dir)
        uninstall_src = INSTALLER_DIR / "uninstall.bat"
        if uninstall_src.exists():
            shutil.copy2(uninstall_src, target_root / "uninstall.bat")
        cfg_desktop = write_config(target_dir, style)
        if cfg_desktop and str(cfg_desktop) not in results["configs"]:
            results["configs"].append(str(cfg_desktop))
        results["desktop_dir"] = str(target_dir)
        for item in sorted(target_dir.rglob("*")):
            if item.is_file():
                results["files"].append(str(item))

        if enable_startup:
            python_exe = ensure_python()
            script = target_dir / "deepseek_price_alert.py"
            cmd = [python_exe, str(script), "--setup-startup"]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=30)
                results["startup"] = r.returncode == 0
                if r.stdout:
                    log(f"开机自启输出 / Startup output: {r.stdout.strip()}")
            except Exception as exc:
                log(f"配置开机自启失败 / Startup setup failed: {exc}")
                results["startup"] = False

    return results


# --------------------------------------------------------------------------
# HTTP 服务 / HTTP server
# --------------------------------------------------------------------------
class InstallerHandler(BaseHTTPRequestHandler):
    server_version = f"DeepSeekPriceAlertInstaller/{VERSION}"

    def log_message(self, fmt, *args):
        log(f"[http] {self.address_string()} - {fmt % args}")

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_page(self):
        try:
            content = PAGE_FILE.read_bytes()
        except OSError:
            content = ("<html><body><h1>installer.html 未找到 / Not found</h1>"
                       "<p>请确保 installer.html 与 installer.py 在同一目录。</p>"
                       "</body></html>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_extra_page(self, rel_path: str):
        """
        附带的风格页（style_preview.html / style_picker.html）。
        v0.9.3：安装向导里可以直接打开它们，装完再想改风格也不用去翻文件夹。
        """
        target = INSTALLER_DIR / "desktop" / rel_path
        if not target.exists():
            target = INSTALLER_DIR / rel_path
        try:
            content = target.read_bytes()
        except OSError:
            content = (f"<html><body><h1>{html.escape(rel_path)} 未找到 / Not found</h1>"
                       "<p>安装包可能不完整，请重新解压。</p></body></html>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_page()
        elif self.path in ("/style_preview", "/style_preview.html"):
            self._send_extra_page("style_preview.html")
        elif self.path in ("/style_picker", "/style_picker.html"):
            self._send_extra_page("style_picker.html")
        elif self.path == "/health":
            self._send_json({"ok": True, "version": VERSION})
        elif self.path == "/api/info":
            self._send_json({
                "version": VERSION,
                "desktop_exists": SOURCE_DESKTOP.exists(),
                "workbuddy_exists": (INSTALLER_DIR / "skill").exists(),
                "style_choices": {k: sorted(v) for k, v in STYLE_CHOICES.items()},
                "style_defaults": STYLE_DEFAULTS,
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/install":
            self._send_json({"error": "not found"}, 404)
            return

        # 读取请求体
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            self._send_json({"error": f"无效请求: {exc}"}, 400)
            return

        edition = payload.get("edition", "")
        enable_startup = bool(payload.get("enable_startup", False))
        also_desktop = bool(payload.get("also_desktop", False))
        cleanup = bool(payload.get("cleanup", True))
        custom_dir = (payload.get("install_dir") or "").strip()
        style = payload.get("style")  # 未动风格区时前端不会传，此时保留用户已有配置

        # 校验版本选择
        if edition not in ("desktop", "workbuddy"):
            self._send_json({"error": f"未知版本: {edition}"}, 400)
            return

        # 目标根目录（允许自定义，默认用户主目录）
        target_root = Path(custom_dir) if custom_dir else DEFAULT_TARGET_ROOT
        try:
            target_root = target_root.expanduser().resolve()
            target_root.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self._send_json({"error": f"无法创建安装目录: {exc}"}, 400)
            return

        try:
            if edition == "desktop":
                result = install_desktop(target_root, enable_startup, style)
            else:
                result = install_workbuddy(target_root, also_desktop, enable_startup, style)

            # 安装成功后，若用户选择"自动删除安装包"，则清理 ZIP 与解压目录
            cleaned = {}
            if cleanup:
                cleaned = cleanup_installer(remove_zip=True)
                result["cleaned"] = cleaned

            self._send_json({"ok": True, "result": result})
        except Exception as exc:
            log(f"安装失败 / Install failed: {exc}")
            self._send_json({"ok": False, "error": str(exc)}, 500)


# --------------------------------------------------------------------------
# 入口 / Main
# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek 降价提醒工具 二合一安装向导")
    parser.add_argument("--port", type=int, default=8765, help="本地端口 (默认 8765)")
    parser.add_argument("--test", action="store_true", help="自检模式：不打开浏览器")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器（由外部脚本打开）")
    args = parser.parse_args()

    if not PAGE_FILE.exists():
        print(f"❌ 未找到 installer.html（当前目录: {INSTALLER_DIR}）")
        return 1

    # 端口被占用（常见于上一次安装窗口没关）时自动往后顺延，最多试 10 个
    server = None
    port = args.port
    last_exc = None
    for candidate in range(args.port, args.port + 10):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), InstallerHandler)
            port = candidate
            break
        except OSError as exc:
            last_exc = exc
    if server is None:
        print("=" * 60)
        print(f"[错误] 无法在 127.0.0.1:{args.port} ~ {args.port + 9} 之间启动安装服务。")
        print(f"       最后一个原因代码: {last_exc}")
        print("       可能被其它程序占用，或被安全软件拦截。")
        print("       请关掉其它安装窗口后重试。")
        print("=" * 60)
        return 2
    url = f"http://127.0.0.1:{port}/"

    log("=" * 60)
    log("DeepSeek 降价提醒工具 二合一安装向导")
    log(f"版本 / Version: {VERSION}")
    log(f"安装向导地址 / URL: {url}")
    if port != args.port:
        log(f"[提示] 端口 {args.port} 被占用，已自动改用 {port}。")
    log("在页面中选择「桌面通用版」或「WorkBuddy 适配版」完成安装。")
    env_zip = os.environ.get(SETUP_ZIP_ENV, "").strip()
    if env_zip:
        log(f"检测到安装包 / Installer zip: {env_zip}（安装完成后可选自动删除）")
    log("=" * 60)

    # 启动时检查是否有新版本（异步执行，不阻塞安装页面打开）
    try:
        import threading
        threading.Thread(target=check_for_update, daemon=True).start()
    except Exception:
        pass

    if not args.test and not args.no_browser:
        opened = False
        # 方式1（首选）：用 cmd start 打开默认浏览器（最快，不依赖 Python webbrowser）
        try:
            import subprocess
            subprocess.Popen(
                ["cmd", "/c", "start", "", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            opened = True
        except Exception:
            opened = False
        # 方式2（fallback）：Python webbrowser 模块
        if not opened:
            try:
                opened = webbrowser.open(url)
            except Exception:
                opened = False
        if opened:
            log(f"已自动打开浏览器 / Browser opened: {url}")
        else:
            log(f"请手动在浏览器打开 / Please open manually: {url}")
            print(f"👉 如果浏览器未自动打开，请手动访问: {url}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("安装向导已退出 / Installer stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())