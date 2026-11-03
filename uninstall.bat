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
echo   3. 每日定时提醒任务
echo   4. WorkBuddy 技能（如果装过）
echo   5. 本程序所在的整个文件夹
echo.
pause
echo.

echo [1/5] 停止正在运行的程序...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and $_.CommandLine -like '*deepseek_price_alert*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
echo       完成

echo [2/5] 移除开机自启...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\deepseek_price_alert.vbs" (
    del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\deepseek_price_alert.vbs" >nul 2>&1
    echo       已移除
) else (
    echo       没有自启项，跳过
)

echo [3/5] 移除每日定时提醒...
schtasks /Delete /TN "DeepSeekPriceAlertDaily" /F >nul 2>&1
echo       完成（没有该任务时会自动跳过）

echo [4/5] 移除 WorkBuddy 技能...
if exist "%USERPROFILE%\.workbuddy\skills\deepseek-price-alert" (
    rd /s /q "%USERPROFILE%\.workbuddy\skills\deepseek-price-alert" >nul 2>&1
    echo       已移除
) else (
    echo       未安装，跳过
)

rem ==================================================================
rem 关键修复（v0.9.4）：先把自己的工作目录移出待删文件夹。
rem 否则 cmd.exe 的工作目录锁在那个文件夹上，rd 会删光里面的内容，
rem 却删不掉文件夹本身，留下一个空壳 —— 这就是「卸载不彻底、
rem 还要手动再删一次文件夹」的原因。
rem ==================================================================
set "DIR=%~dp0"
if "%DIR:~-1%"=="\" set "DIR=%DIR:~0,-1%"
cd /d "%TEMP%"

echo.
echo [5/5] 删除程序文件夹...
set "CLEANUP=%TEMP%\ds_pa_cleanup.bat"
> "%CLEANUP%" echo @echo off
>> "%CLEANUP%" echo cd /d "%%TEMP%%"
>> "%CLEANUP%" echo ping -n 4 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo ping -n 2 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo ping -n 2 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo ping -n 2 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo ping -n 2 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo ping -n 2 127.0.0.1 ^>nul
>> "%CLEANUP%" echo rd /s /q "%DIR%"
>> "%CLEANUP%" echo del /f /q "%%~f0"
start "" /min "%CLEANUP%"

echo.
echo 卸载完成，文件夹会在几秒内自动删除（最多重试 5 次，防止文件正被占用）。
echo 若 10 秒后文件夹仍然在，多半是杀毒软件正在扫描它，等一会儿再手动删一次即可：
echo   %DIR%
timeout /t 6 >nul
exit
