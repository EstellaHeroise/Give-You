@echo off
rem ============================================================
rem  DeepSeek 降价提醒工具 - 二合一安装向导启动器
rem  双击此文件启动图形安装向导，选择桌面版或 WorkBuddy 版
rem ============================================================
setlocal
cd /d "%~dp0"

rem 自动定位安装包 ZIP（用于安装后自动删除）
rem 优先找解压目录上一级（通常是"下载"文件夹）里本版本的 zip
set "DEEPSEEK_ALERT_SETUP_ZIP="
for %%f in ("%~dp0..\deepseek-price-alert-setup-*.zip") do (
  if not defined DEEPSEEK_ALERT_SETUP_ZIP set "DEEPSEEK_ALERT_SETUP_ZIP=%%~f"
)

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