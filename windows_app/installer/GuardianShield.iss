; Guardian Shield installer (Inno Setup 6). Python is bundled inside GuardianShield.exe - nothing else is needed.
; Silent install:   GuardianShieldSetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
; Options:          /NOAUTOSTART  /NOSITEBLOCK  /NOPOPUPBLOCK  /ALLOW=screenconnect,teamviewer
;                   /PASSWORDHASH=<output of GuardianShield.exe --hash-password>  /DIR="C:\Path"  /LOG="C:\gs.log"
; Silent uninstall: "%ProgramFiles%\Guardian Shield\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART

#define AppVersion "1.1.0"

[Setup]
AppId={{8C5B1F2E-6A4D-4F0B-9E3A-2B7C1D0E5F11}
AppName=Guardian Shield
AppVersion={#AppVersion}
AppVerName=Guardian Shield {#AppVersion}
AppPublisher=Guardian Shield
DefaultDirName={autopf}\Guardian Shield
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=GuardianShieldSetup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=force
RestartApplications=no
SetupLogging=yes
UninstallDisplayName=Guardian Shield
UninstallDisplayIcon={app}\GuardianShield.exe
VersionInfoVersion={#AppVersion}

[Tasks]
Name: "autostart"; Description: "Start Guardian Shield for every user when Windows starts (recommended)"
Name: "siteblock"; Description: "Block known scam websites on this PC (recommended)"
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\dist\GuardianShield.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Guardian Shield"; Filename: "{app}\GuardianShield.exe"
Name: "{autodesktop}\Guardian Shield"; Filename: "{app}\GuardianShield.exe"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "GuardianShield"; ValueData: """{app}\GuardianShield.exe"" --minimized"; Flags: uninsdeletevalue; Check: WantAutostart

[Run]
Filename: "{app}\GuardianShield.exe"; Parameters: "{code:ConfigureArgs}"; Flags: runhidden waituntilterminated; StatusMsg: "Applying protection settings..."
Filename: "{app}\GuardianShield.exe"; Description: "Start Guardian Shield now"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM GuardianShield.exe"; Flags: runhidden waituntilterminated; RunOnceId: "KillApp"
Filename: "{app}\GuardianShield.exe"; Parameters: "--hosts-off"; Flags: runhidden waituntilterminated; RunOnceId: "HostsOff"

[UninstallDelete]
Type: filesandordirs; Name: "{commonappdata}\GuardianShield"

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
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM GuardianShield.exe', '', SW_HIDE, ewWaitUntilTerminated, Code);
end;

function InitializeUninstall(): Boolean;
var
  Code: Integer;
begin
  Result := True;
  // Interactive uninstall asks for the settings password (or a scam check) first. Silent RMM uninstall skips this.
  if not UninstallSilent then
    if Exec(ExpandConstant('{app}\GuardianShield.exe'), '--confirm-uninstall', '', SW_SHOW, ewWaitUntilTerminated, Code) then
      Result := (Code = 0);
end;
