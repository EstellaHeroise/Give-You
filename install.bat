@echo off
chcp 65001 >nul
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

echo.
echo ============================================
echo  DeepSeek 降价提醒 - 安装向导
echo ============================================
echo  正在启动本地安装服务，请稍候...
echo.

rem 检查内置便携 Python 是否存在
if not exist "python\python.exe" (
  echo [错误] 未找到内置 Python：python\python.exe
  echo.
  echo        最常见的原因：只解压了 install.bat 一个文件，或者解压不完整。
  echo        正确做法：右键安装包 ZIP - 全部解压缩 - 再双击解压出来的 install.bat。
  echo.
  echo        当前文件夹：%CD%
  pause
  exit /b 1
)

rem 直接在本窗口运行：所有日志和报错都留在这里，不会一闪就没
"python\python.exe" installer.py
set "EC=%ERRORLEVEL%"

echo.
if not "%EC%"=="0" (
  echo ============================================
  echo  [错误] 安装服务异常退出，错误代码 %EC%
  echo  上面那些文字就是原因，可以直接截图发给作者。
  echo ============================================
  pause
  exit /b %EC%
)

echo  安装向导已关闭。如果页面还没装完，重新双击本文件即可。
pause
endlocal
