[Setup]
AppId={{B84C90F2-8C8B-4A9D-9D36-1F0D6B89A011}
AppName=Advertising & Print ERP Pilot
AppVersion=0.1.0
DefaultDirName={autopf}\AdvertisingPrintERP
DefaultGroupName=Advertising & Print ERP
OutputDir=Output
OutputBaseFilename=AdvertisingPrintERP-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\AdvertisingPrintERP.exe

[Files]
Source: "..\dist\AdvertisingPrintERP\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Advertising & Print ERP"; Filename: "{app}\AdvertisingPrintERP.exe"
Name: "{autodesktop}\Advertising & Print ERP"; Filename: "{app}\AdvertisingPrintERP.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "إنشاء اختصار على سطح المكتب"; Flags: unchecked

[Run]
Filename: "{app}\AdvertisingPrintERP.exe"; Description: "تشغيل البرنامج"; Flags: postinstall nowait
