@echo off
rem ============================================================
rem  DeepSeek 降价提醒工具 - 二合一安装向导启动器
rem  双击此文件启动图形安装向导，选择桌面版或 WorkBuddy 版
rem ============================================================
setlocal
cd /d "%~dp0"

rem 尝试找 python
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py"
)
if not defined PY (
  echo [错误] 未找到 Python。请先安装 Python 3.8+ 并加入 PATH。
  echo [Error] Python not found. Please install Python 3.8+.
  pause
  exit /b 1
)

echo 正在启动 DeepSeek 降价提醒 安装向导...
%PY% installer.py %*
if errorlevel 1 (
  echo.
  echo 安装向导退出异常。请检查上方日志。
  pause
)
endlocal