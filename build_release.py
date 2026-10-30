#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_release.py — 打包二合一安装包
====================================
把以下内容合并为一个 ZIP 安装包（用户只需下载一次）：
  - install.bat          # Windows 双击启动安装向导
  - installer.py         # 安装向导后端
  - installer.html       # 图形选择页面（两个版本卡片）
  - desktop/             # 桌面通用版文件
  - skill/               # WorkBuddy 适配版文件（SKILL.md + 脚本）
  - README.md / LICENSE

用法 / Usage:
  python build_release.py                # 输出到 dist/
  python build_release.py --version 0.5.0

原创使用许可 (Original Works License).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import argparse
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"

# 需要打进安装包的文件（相对于 ROOT）
RELEASE_FILES = [
    "install.bat",
    "installer.py",
    "installer.html",
    "README.md",
    "LICENSE",
    # 桌面通用版（独立程序）
    "desktop/deepseek_price_alert.py",
    "desktop/style_preview.html",
    "desktop/style_picker.html",
    "desktop/README.md",
    "desktop/LICENSE",
    # WorkBuddy 适配版（Skill 完整内容，安装时复制到 ~/.workbuddy/skills）
    "skill/SKILL.md",
    "skill/deepseek_price_alert.py",
    "skill/style_preview.html",
    "skill/style_picker.html",
]


def build(version: str) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_name = f"deepseek-price-alert-setup-{version}.zip"
    zip_path = DIST_DIR / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in RELEASE_FILES:
            src = ROOT / rel
            if not src.exists():
                print(f"⚠️ 跳过缺失文件 / Skipping missing: {rel}")
                continue
            zf.write(src, arcname=rel)
            print(f"📦 打包 / Packed: {rel} ({src.stat().st_size} B)")

        # 写一个构建信息文件
        info = (
            f"DeepSeek Price Alert - 二合一安装包\n"
            f"Version: {version}\n"
            f"Built: {datetime.now().isoformat(timespec='seconds')}\n"
            f"Contains: Desktop Edition + WorkBuddy Edition\n"
        )
        zf.writestr("BUILD_INFO.txt", info)
        print("📦 打包 / Packed: BUILD_INFO.txt")

    print(f"\n✅ 安装包已生成 / Release zip created: {zip_path}")
    print(f"   大小 / Size: {zip_path.stat().st_size / 1024:.1f} KB")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="打包 DeepSeek 降价提醒 二合一安装包")
    parser.add_argument("--version", default="0.7.0", help="版本号 (默认 0.7.0)")
    args = parser.parse_args()
    build(args.version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())