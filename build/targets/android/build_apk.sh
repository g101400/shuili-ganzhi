#!/usr/bin/env bash
# 编译 水利感知项目一张图 Android APK（WebApp 外壳，内嵌 webroot）
# 用法（Git Bash）：
#   bash build_apk.sh                    # 有签名配置则发布签名，否则 debug 签名（均可安装）
#   SHUILI_KEYSTORE_PROPS=/e/dev/ganzhi/tools/keystore/keystore.properties bash build_apk.sh
# 铁律：路径由脚本位置锚定（禁 CWD 依赖）；密钥零入库（keystore/口令文件在仓库外）；
#       assets/www 由本脚本从 webroot 同步再生，不入库。
set -e

# 自包含：路径基于脚本位置推导
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"   # build/targets/android
REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"     # 工程根
SOURCE="$REPO/webroot"                         # Web 源 = webroot 基线
PROJECT="$SCRIPT_DIR"                          # 自包含安卓工程
ASSETS="$PROJECT/app/src/main/assets/www"      # 由本脚本同步再生
RELEASE_DIR="$REPO/releases/android"
# 工具链：可经环境变量覆盖（默认本机 E 盘位置；缺失时请自行设置 JDK/GRADLE）
TOOLS="${TOOLS:-/e/dev/ganzhi/tools}"
JDK="${JDK:-/c/Program Files/Microsoft/jdk-17.0.20.101-hotspot}"
GRADLE="${GRADLE:-$TOOLS/gradle-8.10.2/bin/gradle}"

export JAVA_HOME="$JDK"
export PATH="$JDK/bin:$PATH"

echo "[1/3] 同步 webroot 到 APK 资源目录..."
rm -rf "$ASSETS"; mkdir -p "$ASSETS"
tar -C "$SOURCE" -cf - . | ( cd "$ASSETS" && tar -xf - )

echo "[2/3] 编译 APK（gradle assembleRelease）..."
# --no-daemon 规避 Windows Gradle 守护进程残留文件锁；签名由 app/build.gradle 决策：
# SHUILI_KEYSTORE_PROPS（或 build/targets/android/keystore.properties）存在 → 发布签名；否则 debug 签名
"$GRADLE" --no-daemon -p "$PROJECT" clean assembleRelease

echo "[3/3] 取出 APK..."
APK=$(find "$PROJECT/app/build/outputs/apk/release" -name '*.apk' | head -1)
VER=$(python -c "import json,io;print(json.load(io.open('$SOURCE/version.json',encoding='utf-8'))['version'])" 2>/dev/null || echo "1.77")
mkdir -p "$RELEASE_DIR"
cp "$APK" "$RELEASE_DIR/水利感知项目一张图_V${VER}.apk"
echo "完成 -> $RELEASE_DIR/水利感知项目一张图_V${VER}.apk"
ls -lh "$RELEASE_DIR/水利感知项目一张图_V${VER}.apk"
