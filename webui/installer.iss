; Kronos WebUI - Inno Setup 安装脚本
; 用法：在 build.bat 中由 ISCC.exe 自动调用

#define AppName      "Kronos WebUI"
#define AppVersion   "1.0.0"
#define AppPublisher "Kronos Project"
#define AppURL       "https://github.com/liyong763435720/Kronos-cn"
#define AppExeName   "KronosWebUI.exe"
#define DistDir      "dist\KronosWebUI"

[Setup]
AppId={{8F3A2B1C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; 压缩设置（fast 模式减少临时空间占用）
Compression=lzma2/fast
SolidCompression=no
; 输出
OutputDir=dist
OutputBaseFilename=KronosWebUI_Setup
; 用户级安装，无需管理员权限，避免 Program Files 写入限制
PrivilegesRequired=lowest
; 向导样式
WizardStyle=modern
; 最低 Windows 版本：Windows 10
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "创建桌面快捷方式";     GroupDescription: "附加图标："; Flags: checkedonce
Name: "quicklaunchicon"; Description: "创建快速启动快捷方式"; GroupDescription: "附加图标："; Flags: unchecked

[Files]
; 复制整个 PyInstaller 输出目录
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单
Name: "{group}\{#AppName}";          Filename: "{app}\{#AppExeName}"; Comment: "启动 Kronos 金融预测 Web 界面"
Name: "{group}\卸载 {#AppName}";     Filename: "{uninstallexe}"
; 桌面
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
; 快速启动
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后可选择立即启动
Filename: "{app}\{#AppExeName}"; Description: "立即启动 {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时清理用户生成的数据文件（可选，注释掉则保留）
; Type: filesandordirs; Name: "{app}\data"
; Type: filesandordirs; Name: "{app}\prediction_results"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
// 安装前检查：若旧版正在运行则提示关闭
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
