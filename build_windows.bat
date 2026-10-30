@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHON=py -3"
if exist "runtime\python\python.exe" set "PYTHON=runtime\python\python.exe"
%PYTHON% -m venv .build-venv
if errorlevel 1 goto failed
.build-venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed
.build-venv\Scripts\python.exe tools\fetch_windows_bins.py
if errorlevel 1 goto failed
.build-venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name "CN视频下载器" --collect-all customtkinter --distpath dist\windows-build app\main.py
if errorlevel 1 goto failed
xcopy /E /I /Y runtime "dist\windows-build\CN视频下载器\runtime"
if errorlevel 1 goto failed
echo 构建完成：dist\windows-build\CN视频下载器\CN视频下载器.exe
pause
exit /b 0
:failed
echo 构建失败，请检查上方信息。需要完整 Python 3.11+，包括 Tcl/Tk。
pause
exit /b 1
