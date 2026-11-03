@echo off
chcp 65001 >nul
title 改提醒的样子 - DeepSeek 降价提醒
cd /d "%~dp0"

if not exist "desktop\style_tool.py" (
  echo.
  echo [提示] 没找到 desktop\style_tool.py
  echo        本程序只随「桌面通用版」安装。你装的可能是纯 WorkBuddy 技能版，
  echo        那种情况请直接编辑技能目录里的 config.json。
  echo.
  echo        当前文件夹：%CD%
  pause
  exit /b 1
)

if not exist "desktop\python\python.exe" (
  echo.
  echo [提示] 没找到内置 Python：desktop\python\python.exe
  echo        说明安装不完整，重新跑一次安装包即可。
  echo.
  pause
  exit /b 1
)

"desktop\python\python.exe" "desktop\style_tool.py"

echo.
echo 窗口可以关掉了。
timeout /t 3 >nul
