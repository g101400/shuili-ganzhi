# 水利感知项目一张图 · 一键四端构建（本机权威入口）
# 用法：
#   powershell -File build\build_all.ps1            # 全平台：Win(exe+msi) + UOS deb×3 + Android + iOS PWA + 门禁
#   powershell -File build\build_all.ps1 -Only web   # 仅 Web 冒烟（http.server 自检）
#   powershell -File build\build_all.ps1 -Only win / uos / android / ios / gate
# 铁律：PROJECT_ROOT 由本脚本绝对位置锚定（禁 CWD 相对路径）；出包前清同版本旧包；
#       每步失败即中止（不吞错）；产物一律落 releases\。
param([ValidateSet("all","web","win","uos","android","ios","gate")][string]$Only = "all")

$ErrorActionPreference = "Stop"
# ---- PROJECT_ROOT 锚定（防 CWD 假绿）----
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot        # build\ -> 工程根
$TOOLS        = "E:\dev\ganzhi\tools"
$WIX          = "$TOOLS\dotnet-home\.dotnet\tools\wix.exe"
$GRADLE       = "$TOOLS\gradle-8.10.2\bin\gradle.bat"
$RELEASES     = "$PROJECT_ROOT\releases"

# ---- 环境重定向（全落 E 盘）----
$env:JAVA_HOME         = "C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\"
$env:GRADLE_USER_HOME  = "$TOOLS\gradle-home"
$env:ANDROID_HOME      = "$TOOLS\android-sdk"
$env:ANDROID_SDK_ROOT  = "$TOOLS\android-sdk"
$env:NUGET_PACKAGES    = "$TOOLS\nuget-packages"
$env:DOTNET_CLI_HOME   = "$TOOLS\dotnet-home"
$env:WIX_EXTENSIONS_DIR= "$TOOLS\wix-extensions"
$env:Path              = "$env:JAVA_HOME\bin;$env:Path"

function Step($name, $script) {
    Write-Host "`n==> [$name]" -ForegroundColor Cyan
    & $script
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "[$name] 失败 exit=$LASTEXITCODE" }
}

$t = @{}
$t.all = $Only -eq "all"

# ---------- 0) Web 冒烟 ----------
if ($t.all -or $Only -eq "web") {
    Step "Web 冒烟" {
        $proc = Start-Process python -ArgumentList "-m","http.server","8080","-d","$PROJECT_ROOT\webroot" -WindowStyle Hidden -PassThru
        Start-Sleep 2
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:8080/index.html" -UseBasicParsing -TimeoutSec 10
            if ($r.StatusCode -ne 200) { throw "HTTP $($r.StatusCode)" }
            Write-Host "  http://localhost:8080 -> 200 OK（地图/菜单人工复核入口）"
        } finally { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
    }
}

# ---------- 1) Windows exe ----------
if ($t.all -or $Only -eq "win") {
    Step "Win exe（dotnet publish 单文件）" {
        $shellWww = "$PROJECT_ROOT\native-shell\win-webview2\webroot"
        if (Test-Path $shellWww) { Remove-Item $shellWww -Recurse -Force }
        Copy-Item "$PROJECT_ROOT\webroot" $shellWww -Recurse
        dotnet publish "$PROJECT_ROOT\native-shell\win-webview2\ShuiliMap.csproj" -c Release -r win-x64 -o "$RELEASES\win" | Out-Null
        if (-not (Test-Path "$RELEASES\win\水利感知项目一张图.exe")) { throw "exe 未产出" }
        Write-Host ("  exe -> {0} ({1:N2} MB)" -f "$RELEASES\win\水利感知项目一张图.exe", ((Get-Item "$RELEASES\win\水利感知项目一张图.exe").Length/1MB))
    }
    Step "Win msi（WiX v7）" {
        powershell -File "$PROJECT_ROOT\build\build_msi.ps1"
    }
}

# ---------- 2) UOS deb ×3 ----------
if ($t.all -or $Only -eq "uos") {
    foreach ($arch in "amd64","arm64","mips64el") {
        Step "UOS deb ($arch)" {
            python "$PROJECT_ROOT\build\build_deb_pure.py" $arch
            if ($LASTEXITCODE -ne 0) { throw "deb $arch 失败" }
        }
    }
}

# ---------- 3) Android APK ----------
if ($t.all -or $Only -eq "android") {
    Step "Android APK（gradle assembleRelease）" {
        $assets = "$PROJECT_ROOT\build\targets\android\app\src\main\assets\www"
        if (Test-Path $assets) { Remove-Item $assets -Recurse -Force }
        New-Item -ItemType Directory -Force -Path $assets | Out-Null
        Copy-Item "$PROJECT_ROOT\webroot\*" $assets -Recurse
        # 发布签名（密钥零入库）：keystore.properties 在仓库外 tools\keystore\，存在则注入；
        # 不存在时 build.gradle 自动降级 debug 签名（仍为 release APK）
        $ksPropsPath = "$TOOLS\keystore\keystore.properties"
        if (Test-Path $ksPropsPath) { $env:SHUILI_KEYSTORE_PROPS = $ksPropsPath }
        Push-Location "$PROJECT_ROOT\build\targets\android"
        try {
            & $GRADLE --no-daemon -p . clean assembleRelease | Select-Object -Last 3
            if ($LASTEXITCODE -ne 0) { throw "gradle 失败" }
        } finally { Pop-Location }
        $apk = Get-ChildItem "$PROJECT_ROOT\build\targets\android\app\build\outputs\apk\release" -Filter *.apk | Select-Object -First 1
        New-Item -ItemType Directory -Force -Path "$RELEASES\android" | Out-Null
        Copy-Item $apk.FullName "$RELEASES\android\水利感知项目一张图_V1.76.apk" -Force
        Write-Host ("  APK -> {0} ({1:N2} MB)" -f "$RELEASES\android\水利感知项目一张图_V1.76.apk", ($apk.Length/1MB))
    }
}

# ---------- 4) iOS PWA ----------
if ($t.all -or $Only -eq "ios") {
    Step "iOS PWA zip" {
        python "$PROJECT_ROOT\build\build_ios_pwa.py"
        if ($LASTEXITCODE -ne 0) { throw "iOS PWA 失败" }
    }
}

# ---------- 5) 回归门禁 ----------
if ($t.all -or $Only -eq "gate") {
    Step "回归门禁（11 项断言）" {
        python "$PROJECT_ROOT\build\gate_check.py"
        if ($LASTEXITCODE -ne 0) { throw "门禁未全过（防假绿）" }
    }
}

Write-Host "`n==== 全部完成：产物清单 ====" -ForegroundColor Green
Get-ChildItem $RELEASES -Recurse -File |
    Where-Object { $_.FullName -notmatch "_msi" } |
    ForEach-Object { Write-Host ("  {0,-58} {1,8:N2} MB" -f $_.FullName.Replace("$RELEASES\",""), ($_.Length/1MB)) }
