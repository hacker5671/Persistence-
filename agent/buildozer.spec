[app]

# (str) Title of your application
title = SpyAgent

# (str) Package name
package.name = spyagent

# (str) Package domain (reverse DNS)
package.domain = org.test

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Requirements – include only what's needed
requirements = python3,kivy,opencv-python,numpy,Pillow,requests

# (str) Android API level
android.api = 33

# (str) Minimum Android API
android.minapi = 21

# (list) Android permissions
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,WAKE_LOCK

# (bool) Enable Android services
android.allow_background_service = True

# (bool) Keep the app running in background
android.foreground = True

# (str) Android manifest (optional – custom)
# android.manifest = android/AndroidManifest.xml

# (bool) Enable Gradle build
android.gradle_dependencies = True

# (list) Java classes to add
# android.add_src =

# (list) Android libraries to add
# android.add_libs =

# (list) Assets to add
# android.add_assets =

# (list) Python modules to copy
# android.add_python_modules =

# (str) Fullscreen mode
fullscreen = 1

# (str) Orientation
orientation = portrait

# (bool) Enable/disable logcat logs
android.logcat = True

[buildozer]

# (int) Log level (0=debug, 1=info, 2=warning, 3=error, 4=critical)
log_level = 2

# (bool) Warn if root is required
warn_on_root = 0

# (bool) Automatically accept SDK licenses
android.accept_sdk_license = True

# (str) Android NDK version
android.ndk = 23b

# (str) Android SDK version
android.sdk = 33

# (str) Android platform
android.platform = 33

# (str) Android build tools version
android.build_tools = 30.0.3

# (bool) Enable APK splitting
android.enable_apk_splitting = False