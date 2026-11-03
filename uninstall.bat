@echo off
chcp 65001 >nul
title DeepSeek 降价提醒工具 - 卸载
echo ============================================
echo   DeepSeek 降价提醒工具 - 卸载程序
echo ============================================
echo.
echo 将要清理以下内容：
echo   1. 正在运行的本工具进程（不会影响其它 Python 程序）
echo   2. 开机自启项
echo   3. WorkBuddy 技能（如果装过）
echo   4. 本程序所在的整个文件夹
echo.
pause
echo.

echo [1/4] 停止正在运行的程序...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and $_.CommandLine -like '*deepseek_price_alert*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo       完成

echo [2/4] 移除开机自启...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\deepseek_price_alert.vbs" (
    del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\deepseek_price_alert.vbs" >nul 2>&1
    echo       已移除
) else (
    echo       没有自启项，跳过
)

echo [3/4] 移除每日定时提醒...
schtasks /Delete /TN "DeepSeekPriceAlertDaily" /F >nul 2>&1

echo [4/4] 移除 WorkBuddy 技能...
if exist "%USERPROFILE%\.workbuddy\skills\deepseek-price-alert" (
    rd /s /q "%USERPROFILE%\.workbuddy\skills\deepseek-price-alert" >nul 2>&1
    echo       已移除
) else (
    echo       未安装，跳过
)

echo.
echo 正在删除程序文件夹...
set "DIR=%~dp0"
if "%DIR:~-1%"=="\" set "DIR=%DIR:~0,-1%"
set "CLEANUP=%TEMP%\ds_pa_cleanup.bat"
> "%CLEANUP%" echo @echo off
>> "%CLEANUP%" echo ping -n 3 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo del /f /q "%%~f0"
start "" /min "%CLEANUP%"

echo.
echo 卸载完成，文件夹会在 2 秒内自动删除。
echo 如果没删掉，手动删掉这个文件夹即可：%DIR%
timeout /t 4 >nul
exit
