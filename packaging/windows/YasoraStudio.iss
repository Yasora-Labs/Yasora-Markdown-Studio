#define MyAppName "Yasora Markdown Studio"
#define MyAppVersion "0.4.0"
#define MyExe "YasoraMarkdownStudio.exe"
[Setup]
AppId={{9BC4BC38-9D82-4AA7-B4C9-D3AC34727071}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Yasora-Labs
AppPublisherURL=https://github.com/Yasora-Labs/Yasora-Markdown-Studio
AppSupportURL=https://github.com/Yasora-Labs/Yasora-Markdown-Studio/issues
DefaultDirName={localappdata}\Programs\Yasora Markdown Studio
DefaultGroupName=Yasora Markdown Studio
OutputDir=..\..\dist\release
OutputBaseFilename=Yasora-Studio-Windows-x64-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyExe}
ChangesAssociations=yes
DisableDirPage=no
WizardStyle=modern
[Tasks]
Name: desktopicon; Description: "Create desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: contextmenu; Description: "Add 'Convert to Markdown (Yasora)' to Explorer right-click menus"; GroupDescription: "Windows Explorer integration:"; Flags: checkedonce
[Files]
Source: "..\..\dist\YasoraMarkdownStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{userprograms}\Yasora Markdown Studio"; Filename: "{app}\{#MyExe}"; WorkingDir: "{app}"
Name: "{userdesktop}\Yasora Markdown Studio"; Filename: "{app}\{#MyExe}"; Tasks: desktopicon
[Registry]
Root: HKCU; Subkey: "Software\Classes\*\shell\YasoraMarkdownStudio"; ValueType: string; ValueName: ""; ValueData: "Convert to Markdown (Yasora)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\YasoraMarkdownStudio"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyExe},0"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\YasoraMarkdownStudio\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyExe}"" --convert ""%1"""; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\YasoraMarkdownStudio"; ValueType: string; ValueName: ""; ValueData: "Convert folder to Markdown (Yasora)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\YasoraMarkdownStudio"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyExe},0"; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\Directory\shell\YasoraMarkdownStudio\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyExe}"" --convert ""%1"""; Tasks: contextmenu
[Run]
Filename: "{app}\{#MyExe}"; Description: "Launch Yasora Markdown Studio"; Flags: nowait postinstall skipifsilent
