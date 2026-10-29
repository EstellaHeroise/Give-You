#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

用法 / Usage:
  python installer.py            # 启动安装向导（默认端口 8765）
  python installer.py --port 9000
  python installer.py --test     # 自检模式：不打开浏览器，仅启动服务供测试

MIT License.
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
VERSION = "0.5.0"

# 安装目标根目录（默认在用户主目录下，两版本子目录分离，互不冲突）
DEFAULT_TARGET_ROOT = Path.home() / "deepseek-price-alert"

# 两个版本的目标子目录
DESKTOP_SUBDIR = "desktop"
WORKBUDDY_SUBDIR = "workbuddy"

# 源文件目录（安装包内的目录）
SOURCE_DESKTOP = INSTALLER_DIR / "desktop"
SOURCE_WORKBUDDY = INSTALLER_DIR / "workbuddy"

# WorkBuddy skills 目录（用户级）
WORKBUDDY_SKILLS_DIR = Path.home() / ".workbuddy" / "skills" / "deepseek-price-alert"

# 安装日志（写入系统临时目录，便于排查）
LOG_PATH = Path(tempfile.gettempdir()) / "deepseek_installer.log"

# 页面文件
PAGE_FILE = INSTALLER_DIR / "installer.html"


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


# --------------------------------------------------------------------------
# 安装逻辑 / Install logic
# --------------------------------------------------------------------------
def install_desktop(target_root: Path, enable_startup: bool) -> dict:
    """
    安装桌面通用版。
    1. 复制 desktop/ 下的文件到 <target_root>/desktop
    2. 可选：配置开机自启（调用主脚本 --setup-startup）
    """
    target_dir = target_root / DESKTOP_SUBDIR
    target_dir.mkdir(parents=True, exist_ok=True)

    copy_tree(SOURCE_DESKTOP, target_dir)

    results = {
        "version": "桌面通用版 / Desktop Edition",
        "install_dir": str(target_dir),
        "startup": False,
        "files": [],
    }

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
                      enable_startup: bool) -> dict:
    """
    安装 WorkBuddy 适配版。
    1. 复制 skill/ 到 WorkBuddy 用户级 skills 目录（~/.workbuddy/skills/deepseek-price-alert）
    2. 若 also_desktop 为真，同时把桌面版程序复制到 <target_root>/desktop（联动版）
    3. 可选：配置开机自启
    """
    results = {
        "version": "WorkBuddy 适配版 / WorkBuddy Edition",
        "skill_dir": str(WORKBUDDY_SKILLS_DIR),
        "desktop_dir": None,
        "startup": False,
        "files": [],
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

    # 2. 可选：同时安装桌面联动版
    if also_desktop:
        target_dir = target_root / DESKTOP_SUBDIR
        target_dir.mkdir(parents=True, exist_ok=True)
        copy_tree(SOURCE_DESKTOP, target_dir)
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
    server_version = "DeepSeekPriceAlertInstaller/0.5"

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

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_page()
        elif self.path == "/health":
            self._send_json({"ok": True, "version": VERSION})
        elif self.path == "/api/info":
            self._send_json({
                "version": VERSION,
                "desktop_exists": SOURCE_DESKTOP.exists(),
                "workbuddy_exists": (INSTALLER_DIR / "skill").exists(),
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
        custom_dir = (payload.get("install_dir") or "").strip()

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
                result = install_desktop(target_root, enable_startup)
            else:
                result = install_workbuddy(target_root, also_desktop, enable_startup)

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
    args = parser.parse_args()

    if not PAGE_FILE.exists():
        print(f"❌ 未找到 installer.html（当前目录: {INSTALLER_DIR}）")
        return 1

    server = ThreadingHTTPServer(("127.0.0.1", args.port), InstallerHandler)
    url = f"http://127.0.0.1:{args.port}/"

    log("=" * 60)
    log("DeepSeek 降价提醒工具 二合一安装向导")
    log(f"版本 / Version: {VERSION}")
    log(f"安装向导地址 / URL: {url}")
    log("在页面中选择「桌面通用版」或「WorkBuddy 适配版」完成安装。")
    log("=" * 60)

    if not args.test:
        try:
            webbrowser.open(url)
        except Exception:
            print(f"请在浏览器中打开: {url}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("安装向导已退出 / Installer stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())