[app]
# (str) Title of your application
title = JennyMonitor

# (str) Package name
package.name = jennymonitor

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,spec

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements (оставляем без изменений)
requirements = python3,kivy,requests,urllib3,chardet,idna

android.meta_data = moe.shizuku.privileged.api.version=3

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# ==========================================================
# Настройки Android (Версия 34 + Авто-лицензии)
# ==========================================================

# (list) Permissions (добавлен POST_NOTIFICATIONS)

android.permissions = INTERNET, POST_NOTIFICATIONS, FOREGROUND_SERVICE, FOREGROUND_SERVICE_SPECIAL_USE, MEDIA_PLAYBACK, SYSTEM_ALERT_WINDOW, WAKE_LOCK, RECEIVE_BOOT_COMPLETED, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, REQUEST_INSTALL_PACKAGES, moe.shizuku.privileged.api

# (int) Target Android API
android.api = 34

# (str) Android build-tools version to use
android.build_tools_version = 34.0.0

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for
android.archs = arm64-v8a

# (bool) Allow backup
android.allow_backup = True

# (str) Logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpyshaerable.so
android.copy_libs = 1

# (str) The name of the main entry point
android.entrypoint = org.kivy.android.PythonActivity

services = monitor:service.py

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
