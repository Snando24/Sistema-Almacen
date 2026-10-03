; Script generado para Inno Setup
; Instala la aplicación R&R Grupo Corporación en Windows

[Setup]
AppId={{F7BD39E5-3DA2-4B19-BB27-6D62EA4F50D0}}
AppName=R&R Grupo Corporación
AppVersion=1.0.0
AppPublisher=R&R Grupo Corporación
AppPublisherURL=https://example.invalid
AppSupportURL=https://example.invalid
AppUpdatesURL=https://example.invalid
DefaultDirName={autopf}\R&R Grupo Corporacion\SisAlmacen
DefaultGroupName=R&R Grupo Corporación
OutputBaseFilename=SisAlmacen-Installer
OutputDir=installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
CreateAppDir=yes
UsePreviousAppDir=no
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\SisAlmacen.exe
InfoBeforeFile=README.txt

[Files]
Source: "dist\SisAlmacen\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\R&R Grupo Corporación"; Filename: "{app}\SisAlmacen.exe"
Name: "{autodesktop}\R&R Grupo Corporación"; Filename: "{app}\SisAlmacen.exe"

[Run]
Filename: "{app}\SisAlmacen.exe"; Description: "Abrir R&R Grupo Corporación"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{uninstallexe}"; Parameters: "/VERYSILENT /NORESTART"; Flags: waituntilterminated
