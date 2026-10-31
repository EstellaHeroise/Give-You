#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本保留脚本（GitHub 只留 0.8.0 + 最新版；本地工程文件夹全留）。

规则：
  1. 基线版 0.8.0 永远保留在仓库里。
  2. 最新版永远保留在仓库里。
  3. 其余 setup zip 移到本地 _archive/ 目录（_archive/ 已在 .gitignore 中，不会被推上 GitHub）。

用法（在仓库根目录，tool-deepseek 分支）：
    python prune_releases.py           # 执行归档
    python prune_releases.py --dry-run  # 只看要动哪些，不动手
"""

import os
import re
import shutil
import sys
from pathlib import Path

KEEP_BASE = "0.8.0"          # 基线版本，永远不归档
PATTERN = re.compile(r"^deepseek-price-alert-setup-(\d+\.\d+\.\d+)\.zip$")
ARCHIVE_DIR = Path("_archive")


def parse_ver(s):
    return tuple(int(x) for x in s.split("."))


def main():
    dry = "--dry-run" in sys.argv
    root = Path(__file__).resolve().parent

    found = []
    for p in root.glob("deepseek-price-alert-setup-*.zip"):
        m = PATTERN.match(p.name)
        if m:
            found.append((m.group(1), p))

    if not found:
        print("[prune] 仓库根目录没有找到 setup 安装包，无事可做。")
        return 0

    found.sort(key=lambda t: parse_ver(t[0]))
    versions = [v for v, _ in found]
    latest = versions[-1]

    keep = {KEEP_BASE, latest}
    to_archive = [(v, p) for v, p in found if v not in keep]

    print(f"[prune] 发现版本: {', '.join(versions)}")
    print(f"[prune] 保留在仓库: {', '.join(sorted(keep, key=parse_ver))}")

    if not to_archive:
        print("[prune] 没有需要归档的旧版本。")
        return 0

    if not dry:
        ARCHIVE_DIR.mkdir(exist_ok=True)

    for v, p in to_archive:
        dest = ARCHIVE_DIR / p.name
        if dry:
            print(f"[dry-run] 将归档 {p.name} -> {dest}")
        else:
            if dest.exists():
                dest.unlink()
            shutil.move(str(p), str(dest))
            print(f"[prune] 已归档 {p.name} -> {dest}")

    if not dry:
        print("[prune] 完成。_archive/ 已被 .gitignore 忽略，不会推到 GitHub。")
        print("[prune] 记得 git add -A && git commit，把删除动作提交上去。")
    return 0


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    sys.exit(main())
