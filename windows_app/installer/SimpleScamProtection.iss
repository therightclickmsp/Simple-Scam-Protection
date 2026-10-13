; Simple Scam Protection installer (Inno Setup 6). Python is bundled inside SimpleScamProtection.exe - nothing else is needed.
; Silent install:   SimpleScamProtectionSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
; Options:          /NOAUTOSTART  /NOSITEBLOCK  /NOPOPUPBLOCK  /ALLOW=screenconnect,teamviewer
;                   /PASSWORDHASH=<output of SimpleScamProtection.exe --hash-password>  /DIR="C:\Path"  /LOG="C:\gs.log"
; Silent uninstall: "%ProgramFiles%\Simple Scam Protection\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART

#ifndef AppVersion
  #define AppVersion "1.2.0"
#endif

[Setup]
AppId={{8C5B1F2E-6A4D-4F0B-9E3A-2B7C1D0E5F11}
AppName=Simple Scam Protection
AppVersion={#AppVersion}
AppVerName=Simple Scam Protection {#AppVersion}
AppPublisher=Simple Scam Protection
DefaultDirName={autopf}\Simple Scam Protection
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=SimpleScamProtectionSetup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=force
RestartApplications=no
SetupLogging=yes
UninstallDisplayName=Simple Scam Protection
UninstallDisplayIcon={app}\SimpleScamProtection.exe
VersionInfoVersion={#AppVersion}

[Tasks]
Name: "autostart"; Description: "Start Simple Scam Protection for every user when Windows starts (recommended)"
Name: "siteblock"; Description: "Block known scam websites on this PC (recommended)"
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\dist\SimpleScamProtection.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Simple Scam Protection"; Filename: "{app}\SimpleScamProtection.exe"
Name: "{autodesktop}\Simple Scam Protection"; Filename: "{app}\SimpleScamProtection.exe"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SimpleScamProtection"; ValueData: """{app}\SimpleScamProtection.exe"" --minimized"; Flags: uninsdeletevalue; Check: WantAutostart

[Run]
Filename: "{app}\SimpleScamProtection.exe"; Parameters: "{code:ConfigureArgs}"; Flags: runhidden waituntilterminated; StatusMsg: "Applying protection settings..."
Filename: "{app}\SimpleScamProtection.exe"; Description: "Start Simple Scam Protection now"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
Filename: "{app}\SimpleScamProtection.exe"; Parameters: "--uninstall-cleanup"; Flags: runhidden waituntilterminated; RunOnceId: "Cleanup"
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM SimpleScamProtection.exe"; Flags: runhidden waituntilterminated; RunOnceId: "KillApp"

[UninstallDelete]
Type: filesandordirs; Name: "{commonappdata}\SimpleScamProtection"

[Code]
function HasSwitch(Name: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), '/' + Name) = 0 then
      Result := True;
end;

function WantAutostart: Boolean;
begin
  Result := WizardIsTaskSelected('autostart') and not HasSwitch('NOAUTOSTART');
end;

function ConfigureArgs(Param: String): String;
var
  V: String;
begin
  Result := '--configure';
  if WizardIsTaskSelected('siteblock') and not HasSwitch('NOSITEBLOCK') then
    Result := Result + ' --site-block'
  else
    Result := Result + ' --no-site-block';
  if HasSwitch('NOPOPUPBLOCK') then
    Result := Result + ' --no-popup-block';
  V := ExpandConstant('{param:PASSWORDHASH|}');
  if V <> '' then
    Result := Result + ' --password-hash "' + V + '"';
  V := ExpandConstant('{param:ALLOW|}');
  if V <> '' then
    Result := Result + ' --allow "' + V + '"';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Code: Integer;
begin
  if CurStep = ssInstall then
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM SimpleScamProtection.exe', '', SW_HIDE, ewWaitUntilTerminated, Code);
end;

function InitializeUninstall(): Boolean;
var
  Code: Integer;
begin
  Result := True;
  // Interactive uninstall asks for the settings password (or a scam check) first. Silent RMM uninstall skips this.
  if not UninstallSilent then
    if Exec(ExpandConstant('{app}\SimpleScamProtection.exe'), '--confirm-uninstall', '', SW_SHOW, ewWaitUntilTerminated, Code) then
      Result := (Code = 0);
end;
