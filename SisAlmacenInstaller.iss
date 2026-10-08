; Instalador de SisAlmacen para Windows

[Setup]
AppId={{F7BD39E5-3DA2-4B19-BB27-6D62EA4F50D0}}
AppName=SisAlmacen
AppVersion=0.1.0
AppVerName=SisAlmacen 0.1.0
AppPublisher=R&R Grupo Corporación
AppPublisherURL=https://example.invalid
AppSupportURL=https://example.invalid
AppUpdatesURL=https://example.invalid
DefaultDirName={autopf}\SisAlmacen
DefaultGroupName=SisAlmacen
SetupIconFile=src\sisalmacen\ui\assets\app_icon.ico
WizardImageFile=src\sisalmacen\ui\assets\installer_wizard.bmp
WizardSmallImageFile=src\sisalmacen\ui\assets\installer_wizard_small.bmp
OutputBaseFilename=SisAlmacen-Installer
OutputDir=installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
CreateAppDir=yes
UsePreviousAppDir=no
DisableProgramGroupPage=no
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\SisAlmacen.exe
InfoBeforeFile=README.txt

[Files]
Source: "dist\SisAlmacen\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SisAlmacen"; Filename: "{app}\SisAlmacen.exe"
Name: "{autodesktop}\SisAlmacen"; Filename: "{app}\SisAlmacen.exe"

[Run]
Filename: "{app}\SisAlmacen.exe"; Description: "Abrir SisAlmacen"; Flags: nowait postinstall skipifsilent
