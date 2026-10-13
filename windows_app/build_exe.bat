@echo off
setlocal
title Guardian Shield - Build
echo ============================================================
echo   Building Guardian Shield for Windows
echo   Everything needed (including Python) is downloaded into
echo   the .build folder next to this file. Nothing else changes.
echo ============================================================
cd /d "%~dp0"
set "BUILD=%~dp0.build"
if not exist "%BUILD%" mkdir "%BUILD%"

set "PY=%BUILD%\python\python.exe"
if exist "%PY%" goto have_python
echo.
echo [1/4] Downloading a private copy of Python 3.12 (only used for building)...
curl -L --fail -o "%BUILD%\python-setup.exe" https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe || goto fail
"%BUILD%\python-setup.exe" /quiet InstallAllUsers=0 TargetDir="%BUILD%\python" Include_launcher=0 InstallLauncherAllUsers=0 Include_test=0 Include_doc=0 PrependPath=0 Shortcuts=0 AssociateFiles=0 || goto fail
if not exist "%PY%" goto fail
:have_python

echo.
echo [2/4] Installing build tools...
"%PY%" -m pip install --upgrade pip --quiet || goto fail
"%PY%" -m pip install -r requirements.txt pyinstaller --quiet || goto fail

echo.
echo [3/4] Building GuardianShield.exe (Python is bundled inside it)...
"%PY%" -m PyInstaller --noconfirm --onefile --windowed --name GuardianShield --hidden-import pystray._win32 run_guardian_shield.py || goto fail

echo.
echo [4/4] Building the installer GuardianShieldSetup.exe...
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" goto have_inno
set "ISCC=%BUILD%\inno\ISCC.exe"
if exist "%ISCC%" goto have_inno
curl -L --fail -o "%BUILD%\innosetup.exe" https://jrsoftware.org/download.php/is.exe || goto fail
"%BUILD%\innosetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER /NOICONS /DIR="%BUILD%\inno" || goto fail
:have_inno
"%ISCC%" installer\GuardianShield.iss || goto fail

echo.
echo ============================================================
echo  Done!
echo   Installer : %~dp0dist\GuardianShieldSetup.exe
echo   Portable  : %~dp0dist\GuardianShield.exe
echo ============================================================
if /i not "%1"=="/quiet" explorer "%~dp0dist"
if /i not "%1"=="/quiet" pause
exit /b 0

:fail
echo.
echo Build failed. See the messages above.
if /i not "%1"=="/quiet" pause
exit /b 1
