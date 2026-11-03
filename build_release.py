#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.10.30
# =====================================================================
"""
build_release.py — 打包二合一安装包
====================================
把以下内容合并为一个 ZIP 安装包（用户只需下载一次）：
  - install.bat          # Windows 双击启动安装向导
  - installer.py         # 安装向导后端
  - installer.html       # 图形选择页面（两个版本卡片）
  - desktop/             # 桌面通用版文件
  - skill/               # WorkBuddy 适配版文件（SKILL.md + 脚本）
  - python/              # 内置便携 Python 运行时（瘦身后的 CPython）
  - prune_releases.py    # 版本保留脚本
  - README.md / LICENSE / BUILD_INFO.txt

用法 / Usage:
  python build_release.py --version 0.9.1
  python build_release.py --version 0.9.1 --python-src "D:\\某处\\python"

原创使用许可 (Original Works License).
本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。
"""

import argparse
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 需要打进安装包的文件/目录（相对于 ROOT）
RELEASE_FILES = [
    "install.bat",
    "uninstall.bat",
    "installer.py",
    "installer.html",
    "prune_releases.py",
    "README.md",
    "LICENSE",
    "BUILD_INFO.txt",
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


def build(version: str, python_src: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"deepseek-price-alert-setup-{version}.zip"

    if not (python_src / "python.exe").exists():
        raise SystemExit(
            f"❌ 找不到内置 Python：{python_src / 'python.exe'}\n"
            f"   请用 --python-src 指定一个包含 python.exe 的便携 Python 目录。"
        )

    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in RELEASE_FILES:
            src = ROOT / rel
            if not src.exists():
                print(f"⚠️ 跳过缺失文件 / Skipping missing: {rel}")
                continue
            zf.write(src, arcname=rel)
            count += 1
            print(f"📦 {rel} ({src.stat().st_size} B)")

        # 内置便携 Python（递归整棵树，跳过 __pycache__ / *.pyc）
        skipped = 0
        for p in sorted(python_src.rglob("*")):
            if not p.is_file():
                continue
            if "__pycache__" in p.parts or p.suffix == ".pyc":
                skipped += 1
                continue
            zf.write(p, arcname=f"python/{p.relative_to(python_src).as_posix()}")
            count += 1
        print(f"🐍 python/ 已打包（跳过缓存 {skipped} 个，累计条目 {count}）")

    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"\n✅ 安装包已生成 / Release zip created: {zip_path}")
    print(f"   大小 / Size: {size_mb:.2f} MB，条目数 / Entries: {count}")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="打包 DeepSeek 降价提醒 二合一安装包")
    parser.add_argument("--version", default="0.9.1", help="版本号 (默认 0.9.1)")
    parser.add_argument(
        "--python-src",
        default=str(ROOT / "python"),
        help="内置便携 Python 目录（包含 python.exe）",
    )
    parser.add_argument("--out", default=str(ROOT), help="输出目录（默认仓库根目录）")
    args = parser.parse_args()

    build(args.version, Path(args.python_src), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
