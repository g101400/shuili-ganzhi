# 水利感知项目一张图 · 一键发版推送（token 零痕迹）
# 用法：
#   $env:GITHUB_TOKEN = "ghp_xxx"   （或 -Token 参数传入；用后建议从会话移除）
#   powershell -File build\push_ready.ps1 -Owner <github用户名> [-Repo shuili-ganzhi] [-Tag v1.76]
# 安全设计（密钥零入库延伸）：
#   1) token 仅存在于本次进程内存：用一次性 URL 推送，不写入 .git/config，不落任何文件；
#   2) 输出统一过滤 token 后再显示（防 git fatal 消息回显 URL 中的 token）；
#   3) 推送前三道预检：工作区干净 / tag 存在 / 已跟踪文件无敏感件。
param(
    [Parameter(Mandatory=$true)][string]$Owner,
    [string]$Repo = "shuili-ganzhi",
    [string]$Branch = "main",
    [string]$Tag = "v1.76",
    [string]$Token = $env:GITHUB_TOKEN
)
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot   # build\ -> 工程根

if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host "!! 未提供 token：请先 \$env:GITHUB_TOKEN = \"ghp_...\" 或用 -Token 传入"; exit 1
}

# ---- 预检1：工作区干净（未提交内容不得随发版外泄）----
$st = git -C $PROJECT_ROOT status --porcelain
if ($LASTEXITCODE -ne 0) { Write-Host "!! git status 失败"; exit 1 }
if ($st) { Write-Host "!! 工作区不干净，先提交："; $st; exit 1 }

# ---- 预检2：tag 存在 ----
$null = git -C $PROJECT_ROOT rev-parse -q --verify "refs/tags/$Tag"
if ($LASTEXITCODE -ne 0) { Write-Host "!! tag $Tag 不存在（先 git tag $Tag）"; exit 1 }

# ---- 预检3：敏感件零入库（文件名级复扫，密钥/口令/keystore）----
$bad = git -C $PROJECT_ROOT ls-files | Select-String -Pattern '(^|/)(ai_seed\.js|secure_boot_cred\.js|sec_crypt\.js)$|\.keystore$|\.jks$|keystore\.properties$|\.github_token$'
if ($bad) { Write-Host "!! 检出敏感件在库，禁止推送："; $bad; exit 1 }

# ---- 推送（一次性 URL；此段临时降 EAP：git 进度走 stderr，PS5.1 下 2>&1 + Stop 会误炸）----
# 低速中止：网络不可达/挂起时 30 秒失败退出（防永久卡死）；真实网络较慢可按需调大
$env:GIT_HTTP_LOW_SPEED_LIMIT = "1000"
$env:GIT_HTTP_LOW_SPEED_TIME  = "30"
$url = "https://$Token@github.com/$Owner/$Repo.git"
$ErrorActionPreference = "Continue"
git -C $PROJECT_ROOT push $url "${Branch}:main" --tags 2>&1 |
    ForEach-Object { ("$_" -replace [regex]::Escape($Token), '***') }
$code = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($code -ne 0) { Write-Host "!! push 失败（exit=$code），核对 token 权限（repo 范围）与仓库名"; exit 1 }

Write-Host "推送完成：$Branch -> github.com/$Owner/$Repo（含 tag $Tag）"
Write-Host "提示：token 未写入任何文件/配置；如需固化 remote：git remote add origin https://github.com/$Owner/$Repo.git（不带 token）"
