@echo off
setlocal
title Simple Scam Protection - Build
echo ============================================================
echo   Building Simple Scam Protection for Windows
echo   Everything needed (including Python) is downloaded into
echo   the .build folder next to this file. Nothing else changes.
echo ============================================================
cd /d "%~dp0"
set "BUILD=%~dp0.build"
set "VERSION=1.3.0"
if not exist "%BUILD%" mkdir "%BUILD%"

set "PY=%BUILD%\python\python.exe"
if exist "%PY%" goto have_python
echo.
echo [1/5] Downloading a private copy of Python 3.12 (only used for building)...
curl -L --fail -o "%BUILD%\python-setup.exe" https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe || goto fail
"%BUILD%\python-setup.exe" /quiet InstallAllUsers=0 TargetDir="%BUILD%\python" Include_launcher=0 InstallLauncherAllUsers=0 Include_test=0 Include_doc=0 PrependPath=0 Shortcuts=0 AssociateFiles=0 || goto fail
if not exist "%PY%" goto fail
:have_python

echo.
echo [2/5] Installing build tools...
"%PY%" -m pip install --upgrade pip --quiet || goto fail
"%PY%" -m pip install -r requirements.txt pyinstaller --quiet || goto fail

echo.
echo [3/5] Building SimpleScamProtection.exe (Python is bundled inside it)...
"%PY%" -m PyInstaller --noconfirm --onefile --windowed --name SimpleScamProtection --hidden-import pystray._win32 run_simple_scam_protection.py || goto fail

echo.
echo [4/5] Building the installer SimpleScamProtectionSetup.exe...
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" goto have_inno
set "ISCC=%BUILD%\inno\ISCC.exe"
if exist "%ISCC%" goto have_inno
curl -L --fail -o "%BUILD%\innosetup.exe" https://jrsoftware.org/download.php/is.exe || goto fail
"%BUILD%\innosetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER /NOICONS /DIR="%BUILD%\inno" || goto fail
:have_inno
"%ISCC%" /DAppVersion=%VERSION% installer\SimpleScamProtection.iss || goto fail

echo.
echo [5/5] Building the MSI SimpleScamProtection.msi (for Intune / Group Policy)...
set "DOTNET_ROOT=%BUILD%\dotnet"
set "PATH=%BUILD%\dotnet;%PATH%"
if exist "%BUILD%\dotnet\dotnet.exe" goto have_dotnet
curl -L --fail -o "%BUILD%\dotnet-install.ps1" https://dot.net/v1/dotnet-install.ps1 || goto fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%BUILD%\dotnet-install.ps1" -Channel 8.0 -InstallDir "%BUILD%\dotnet" || goto fail
:have_dotnet
if exist "%BUILD%\wix\wix.exe" goto have_wix
"%BUILD%\dotnet\dotnet.exe" tool install wix --version 5.0.2 --tool-path "%BUILD%\wix" || goto fail
:have_wix
"%BUILD%\wix\wix.exe" build -arch x64 -d Version=%VERSION% -d ExePath=dist\SimpleScamProtection.exe -o dist\SimpleScamProtection.msi installer\SimpleScamProtection.wxs || goto fail

echo.
echo ============================================================
echo  Done!
echo   Installer : %~dp0dist\SimpleScamProtectionSetup.exe
echo   MSI       : %~dp0dist\SimpleScamProtection.msi
echo   Portable  : %~dp0dist\SimpleScamProtection.exe
echo ============================================================
if /i not "%1"=="/quiet" explorer "%~dp0dist"
if /i not "%1"=="/quiet" pause
exit /b 0

:fail
echo.
echo Build failed. See the messages above.
if /i not "%1"=="/quiet" pause
exit /b 1
