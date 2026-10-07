[app]

# (str) Title of your application
title = Gecord

# (str) Package name
package.name = gecord

# (str) Package domain (needed for android packaging)
package.domain = org.shampooingbon

# (list) Source files to include (let it empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (let it empty to exclude none)
source.exclude_exts = spec

# (list) List of directory to exclude (let it empty to exclude none)
source.exclude_dirs = bin, venv, .git, .github

# (list) Application requirements
requirements = python3,kivy,requests,jnius,certifi,urllib3,idna,charset-normalizer

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (int) Target Android API, should be as high as possible.
android.targetsdk = 36

# (int) Minimum API your APK will support (Android 15, 16 et futurs)
android.minsdk = 35

# (list) Permissions
android.permissions = INTERNET

# (str) Icon of your application
icon.filename = %(source.dir)s/logo.png
