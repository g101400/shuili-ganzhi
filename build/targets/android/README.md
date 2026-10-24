# 水利感知项目一张图 · Android APK

WebView 外壳应用，内嵌 `webroot/`（水利感知项目一张图：视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测，Leaflet 天地图）。

## 目录结构
- `app/src/main/assets/www/` — 内嵌网页（由 `build_all.ps1` 从工程 `webroot/` 同步再生，不入库）
- `app/src/main/java/com/shuili/ganzhi/MainActivity.java` — WebView 加载 `file:///android_asset/www/index.html`
- `app/src/main/AndroidManifest.xml` — 联网/定位权限 + 竖屏，label「水利感知项目一张图」
- `build.gradle` / `app/build.gradle` — AGP 8.5.2，compileSdk/targetSdk 34，minSdk 24，**包名 `com.shuili.ganzhi`，versionCode 76 / versionName 1.76**（与工程根 version.json 同源）

## 本机编译（E盘工具链，全落 E:\dev\ganzhi\tools）
```powershell
powershell -File E:\dev\ganzhi\perc\build\build_all.ps1 -Only android
```
或手动：
```powershell
$env:JAVA_HOME="C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\"
$env:GRADLE_USER_HOME="E:\dev\ganzhi\tools\gradle-home"
$env:ANDROID_HOME="E:\dev\ganzhi\tools\android-sdk"
# 同步 webroot → app\src\main\assets\www 后：
E:\dev\ganzhi\tools\gradle-8.10.2\bin\gradle.bat --no-daemon -p . clean assembleDebug
# 取出：app\build\outputs\apk\debug\app-debug.apk → releases\android\
```

## 签名说明
发布签名 keystore 未随交接包提供（口令走环境变量，不入库）；本地无 keystore 时自动降级 debug 签名，便于构建验证。

## 说明
- 产物归档：`releases/android/水利感知项目一张图_V1.76.apk`（aapt 验证包名/版本）。
- 历史注：本工程自 gujian4060 单体仓库拆分而来，包名已从 `com.gujian.daka` 归位为 `com.shuili.ganzhi`（交接铁律）。

> AI生成
