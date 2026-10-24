# 水利感知项目一张图 · Windows msi 一键构建（WiX v7 方案，全落E盘）
# 用法：powershell -File E:\dev\ganzhi\perc\build\build_msi.ps1
# 前置：wix 工具已装于 E:\dev\ganzhi\tools\dotnet-home\.dotnet\tools\wix.exe（dotnet tool）
#       UI 扩展缓存已 junction 到 E:\dev\ganzhi\tools\wix-extensions
# 说明：wix 对 UI 扩展内置对话框的 (c) 字符报 WIX0311（936 codepage 降级），
#       实测 msi 照常产出且 Dialog 表 21 项完整、cab 36/36 MD5 对账通过——以产物存在为准。
# 注意：PS5.1 下 EAP=Stop + 原生命令 stderr 重定向会把 informational 输出变成终止错误，
#       故本脚本用显式校验（exit码/产物存在）而非 EAP=Stop。
$ErrorActionPreference = "Continue"
$wix = "E:\dev\ganzhi\tools\dotnet-home\.dotnet\tools\wix.exe"
$env:DOTNET_CLI_HOME = "E:\dev\ganzhi\tools\dotnet-home"
$env:NUGET_PACKAGES   = "E:\dev\ganzhi\tools\nuget-packages"
$env:WIX_EXTENSIONS_DIR = "E:\dev\ganzhi\tools\wix-extensions"

$proj    = "E:\dev\ganzhi\perc"
$msiDir  = "$proj\releases\_msi"
$publish = "$proj\releases\win"
$outMsi  = "$publish\水利感知项目一张图_Setup.msi"

# 1) 组装目录（幂等重建）
if (Test-Path $msiDir) { Remove-Item $msiDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $msiDir | Out-Null
Copy-Item "$proj\native-shell\win-webview2\build_msi.wxs" $msiDir
Copy-Item "$proj\native-shell\win-webview2\app.ico" $msiDir

# 2) license.rtf（GBK 编码 RTF，含中文许可声明；wxs 的 WixUILicenseRtf 引用）
$rtf = "{\rtf1\ansi\ansicpg936\deff0{\fonttbl{\f0\fnil\fcharset134 \'cb\'ce\'cc\'e5;}}\fs18\par 水利感知项目一张图 V1.76\par\par \'c8\'ed\'bc\'fe\'d0\'ed\'bf\'c9\'c9\'f9\'c3\'f7\par\par \'b1\'be\'c8\'ed\'bc\'fe\'b9\'e9\'cb\'f9\'d3\'d0\'d5\'df\'cb\'f9\'d3\'d0\'a1\'a3\'b0\'b2\'d7\'b0\'ba\'f3\'bd\'f6\'cf\'de\'b1\'be\'c8\'ed\'bc\'fe\'c4\'da\'b2\'bf\'ca\'b9\'d3\'c3\'a1\'a3\par}"
[IO.File]::WriteAllText("$msiDir\license.rtf", $rtf, [Text.Encoding]::GetEncoding(936))

# 3) files.wxs（纯ASCII Id + $(var.SourceDir) 预处理变量）
python "$proj\build\gen_msi_files.py"
if ($LASTEXITCODE -ne 0) { throw "gen_msi_files.py 失败" }

# 4) 本地化覆盖 + v3 -> v4 语法转换 + Codepage 补丁
$wxl = @'
<WixLocalization xmlns="http://wixtoolset.org/schemas/v4/wxl" Culture="zh-cn" Codepage="936">
  <String Id="LicenseAgreementDlg_Title" Value="许可协议" Overridable="yes" />
  <String Id="LicenseAgreementDlg_LicenseAccepted" Value="我接受许可协议中的条款" Overridable="yes" />
  <String Id="LicenseAgreementDlg_LicenseHyperlink" Value="许可协议" Overridable="yes" />
</WixLocalization>
'@
[IO.File]::WriteAllText("$msiDir\zhcn.wxl", $wxl, [Text.UTF8Encoding]::new($true))

Push-Location $msiDir
try {
    & $wix convert build_msi.wxs files.wxs 2>&1 | Out-Null
    (Get-Content "$msiDir\build_msi.wxs" -Raw) -replace '<Package Name="([^"]+)" Language', '<Package Name="$1" Codepage="936" Language' |
        Set-Content "$msiDir\build_msi.wxs" -Encoding UTF8

    # 5) 构建（WIX0311 为已知非致命降级；成功判据 = msi 实际产出）
    if (Test-Path "$msiDir\_setup.msi") { Remove-Item "$msiDir\_setup.msi" -Force }
    $wixOut = & $wix build -arch x64 "-define" "SourceDir=..\win" -ext "WixToolset.UI.wixext" -culture "zh-cn" -loc "zhcn.wxl" build_msi.wxs files.wxs -out "_setup.msi" 2>&1
    if (Test-Path "$msiDir\_setup.msi") {
        Move-Item "$msiDir\_setup.msi" $outMsi -Force
        Write-Host "msi -> $outMsi ($([math]::Round((Get-Item $outMsi).Length/1MB,2)) MB)"
    } else {
        $wixOut | Select-Object -Last 5 | Write-Host
        throw "wix build 未产出 msi"
    }
} finally { Pop-Location }
