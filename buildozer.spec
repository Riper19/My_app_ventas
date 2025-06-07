[app]
title = Mi Inventario
package.name = miinventario
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,json,kv
version = 1.0
requirements = python3,kivy
orientation = portrait
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/fondo.png
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# --- FIJAR VERSIONES DE ANDROID (SOLUCIÓN AL ERROR DE LICENCIA) ---
android.sdk = 34
android.ndk = 25b
android.build_tools_version = 34.0.0

[buildozer]
log_level = 2
clean_install = True
