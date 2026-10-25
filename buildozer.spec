
[app]

title = Gecord
package.name = gecord
package.domain = org.shampooingbon

source.include_exts = py,png,jpg,jpeg,kv,atlas,json
source.exclude_exts = spec
source.exclude_dirs = bin,venv,.git,.github

requirements = python3,kivy,requests,certifi,urllib3,idna,charset-normalizer

orientation = portrait
fullscreen = 0

android.targetsdk = 36
android.minsdk = 35
android.permissions = INTERNET

icon.filename = %(source.dir)s/logo.png
