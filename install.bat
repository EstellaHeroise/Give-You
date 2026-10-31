@echo off
rem ============================================================
rem  DeepSeek 降价提醒 - 安装向导启动器
rem  双击本文件即可开始安装（内置便携 Python，无需自行安装）
rem ============================================================
setlocal
cd /d "%~dp0"

rem 定位安装包 ZIP（供安装完成后自动清理，可选）
set "DEEPSEEK_ALERT_SETUP_ZIP="
for %%f in ("%~dp0..\deepseek-price-alert-setup-*.zip") do (
  if not defined DEEPSEEK_ALERT_SETUP_ZIP set "DEEPSEEK_ALERT_SETUP_ZIP=%%~f"
)

rem 检查内置便携 Python 是否存在
if not exist "python\python.exe" (
  echo [错误] 未找到内置 Python（python\python.exe）。
  echo        请确认下载的是完整安装包，且未改动文件夹结构。
  pause
  exit /b 1
)

echo.
echo ============================================
echo  DeepSeek 降价提醒 - 安装向导
echo ============================================
echo  正在启动本地安装服务，请稍候...
echo.

rem 用内置 Python 启动安装服务（保留可见窗口，便于排查）
start "" "python\python.exe" installer.py --no-browser

rem 等待本地服务就绪（--noproxy 避免本机访问被代理干扰）
set "READY="
for /l %%i in (1,1,20) do (
  >nul 2>&1 curl -s --noproxy "*" --max-time 1 http://127.0.0.1:8765/health && set "READY=1" && goto :ready
  ping -n 1 127.0.0.1 >nul
)
:ready
if not defined READY (
  echo  [提示] 安装服务暂未响应，仍尝试打开浏览器...
)
ping -n 1 127.0.0.1 >nul

rem 打开浏览器中的图形安装向导
start "" http://127.0.0.1:8765/

echo  若浏览器未自动打开，请手动访问： http://127.0.0.1:8765/
echo  安装向导正在运行，完成后可关闭本窗口。
echo ============================================
echo.

pause
endlocal
