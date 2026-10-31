@echo off
rem ============================================================
rem  DeepSeek Price Alert - Setup Launcher
rem  Double-click this file to start the graphical installer.
rem ============================================================
setlocal
cd /d "%~dp0"

rem Locate the setup ZIP for auto-cleanup after install
set "DEEPSEEK_ALERT_SETUP_ZIP="
for %%f in ("%~dp0..\deepseek-price-alert-setup-*.zip") do (
  if not defined DEEPSEEK_ALERT_SETUP_ZIP set "DEEPSEEK_ALERT_SETUP_ZIP=%%~f"
)

rem Find Python
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py"
)
if not defined PY (
  echo [ERROR] Python not found. Please install Python 3.8+ and add it to PATH.
  pause
  exit /b 1
)

echo.
echo ============================================
echo  DeepSeek Price Alert - Installer
echo ============================================
echo  Starting local web server...
echo  Opening your browser...

rem Start the server in the SAME directory as this bat file, in background
start "" /d "%~dp0" /b %PY% installer.py --no-browser %*

rem Give the server a moment to start
ping -n 3 127.0.0.1 >nul

rem Open the browser
start "" http://127.0.0.1:8765/

echo  If the browser did not open, visit:
echo  http://127.0.0.1:8765/
echo.
echo  The installer is running. Close this window when done.
echo ============================================
echo.

pause
endlocal
