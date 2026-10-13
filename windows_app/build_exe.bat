@echo off
title Guardian Shield - Build
echo ============================================
echo   Building Guardian Shield for Windows
echo ============================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. Get it free from https://www.python.org/downloads/
  echo During setup, tick "Add Python to PATH". Then run this file again.
  pause
  exit /b 1
)
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name GuardianShield --hidden-import pystray._win32 run_guardian_shield.py
if errorlevel 1 (
  echo Build failed. See messages above.
  pause
  exit /b 1
)
echo.
echo Done! Your app is here: %~dp0dist\GuardianShield.exe
explorer "%~dp0dist"
pause
