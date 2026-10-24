# 百度网盘一键发版上传（bypy，零 C 盘：库装 tools\pylibs）
# 用法：
#   powershell -File build\upload_baidupan.ps1
# 首次运行：bypy 打开授权 URL → 浏览器登录百度网盘 → 复制授权码粘贴回终端（此后免授权）。
# 上传布局（与 releases/ 一致）：/apps/bypy/shuili-ganzhi/{win,uos,android,ios}/
# 铁律延伸：仅上传 7 项清单产物（密钥件/keystore/清单外文件一律不上）。
param([string]$RemoteRoot = "/apps/bypy/shuili-ganzhi")

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot          # build\ -> 工程根
$RELEASES     = "$PROJECT_ROOT\releases"
$TOOLS        = "E:\dev\ganzhi\tools"
$PYLIBS       = "$TOOLS\pylibs"
$env:PYTHONPATH = "$PYLIBS;$env:PYTHONPATH"

# ---- 1) bypy 幂等安装（--target 落 E 盘，不污染全局/C盘）----
if (-not (Test-Path "$PYLIBS\bypy")) {
    Write-Host "安装 bypy 到 $PYLIBS ..."
    python -m pip install --target $PYLIBS --quiet bypy
    if ($LASTEXITCODE -ne 0) { throw "bypy 安装失败" }
}
function Bypy { python -m bypy @args; if ($LASTEXITCODE -ne 0) { throw "bypy $args 失败" } }

# ---- 2) 产物清单（与 gate_check/RELEASE_MANIFEST 一致，7 项）----
$V = "1.76"
$items = @(
    @{ local = "win\水利感知项目一张图.exe";                     remote = "win/" },
    @{ local = "win\水利感知项目一张图_Setup.msi";               remote = "win/" },
    @{ local = "uos\shuili-ganzhi_${V}_amd64.deb";              remote = "uos/" },
    @{ local = "uos\shuili-ganzhi_${V}_arm64.deb";              remote = "uos/" },
    @{ local = "uos\shuili-ganzhi_${V}_mips64el.deb";           remote = "uos/" },
    @{ local = "android\水利感知项目一张图_V${V}.apk";           remote = "android/" },
    @{ local = "ios\水利感知项目一张图_V${V}_iOS_PWA.zip";       remote = "ios/" }
)

# ---- 3) 预检：7 产物实存（缺失即中止，防半包发版）----
foreach ($it in $items) {
    if (-not (Test-Path "$RELEASES\$($it.local)")) { throw "产物缺失: $($it.local)" }
}
Write-Host "7 产物预检通过，开始上传 -> $RemoteRoot"

# ---- 4) 逐项上传（bypy 单文件断点续传；目录自动创建）----
$ok = 0
foreach ($it in $items) {
    Write-Host ("上传 {0} -> {1}{2}" -f $it.local, $RemoteRoot, $it.remote)
    Bypy upload "$RELEASES\$($it.local)" "$RemoteRoot$($it.remote)"
    $ok++
}
Write-Host "上传完成 $ok/7"

# ---- 5) 云端对账（列出远端目录树供人工核对大小）----
Write-Host "云端对账："
Bypy list $RemoteRoot
Write-Host "提示：如需严格对账，可按 docs/RELEASE_MANIFEST.md 中的 SHA256 逐个下载复验。"
