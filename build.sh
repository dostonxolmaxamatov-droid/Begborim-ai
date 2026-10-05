#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_SDK_ROOT:?Set ANDROID_SDK_ROOT to your Android SDK directory}"
BT="$ANDROID_SDK_ROOT/build-tools/35.0.0"
JAR="$ANDROID_SDK_ROOT/platforms/android-35/android.jar"
rm -rf build
mkdir -p build/classes build/dex build/generated android/assets
cp server/index.html server/web.js server/web.css server/icon.svg server/manifest.webmanifest server/sw.js server/shirin.js server/shirin.css server/hf-models.js android/assets/
"$BT/aapt2" compile --dir android/res -o build/resources.zip
"$BT/aapt2" link -o build/base.apk -I "$JAR" --manifest android/AndroidManifest.xml --java build/generated -A android/assets build/resources.zip
if [ -n "${ECJ_JAR:-}" ]; then
 java -jar "$ECJ_JAR" -encoding UTF-8 -source 8 -target 8 -classpath "$JAR" -d build/classes android/src/uz/shirin/ai/*.java
else
 javac -encoding UTF-8 -source 8 -target 8 -classpath "$JAR" -d build/classes android/src/uz/shirin/ai/*.java
fi
(cd build/classes && zip -qr ../classes.jar .)
"$BT/d8" --lib "$JAR" --min-api 26 --output build/dex build/classes.jar
cp build/base.apk build/unsigned.apk
(cd build/dex && zip -q -u ../unsigned.apk classes.dex)
"$BT/zipalign" -f 4 build/unsigned.apk build/aligned.apk
if [ ! -f development.keystore ]; then
 keytool -genkeypair -keystore development.keystore -storepass android -keypass android -alias androiddebugkey -dname 'CN=Shirin AI Development' -keyalg RSA -keysize 2048 -validity 10000
fi
"$BT/apksigner" sign --ks development.keystore --ks-pass pass:android --key-pass pass:android --out Shirin-AI.apk build/aligned.apk
"$BT/apksigner" verify --verbose Shirin-AI.apk
