# --- VERSIÓN FINAL Y CORREGIDA ---
[app]

# Título de la aplicación
title = Mi Inventario

# Nombre del paquete (minúsculas, sin espacios)
package.name = miinventario

# Dominio del paquete
package.domain = org.test

# Directorio del código fuente
source.dir = .

# Extensiones de archivo a incluir
source.include_exts = py,png,jpg,jpeg,gif,json,kv

# Versión de la app
version = 1.0

# Librerías necesarias
requirements = python3,kivy

# Orientación de la pantalla
orientation = portrait

# Ícono de la aplicación
icon.filename = %(source.dir)s/icon.png

# Imagen de carga
presplash.filename = %(source.dir)s/fondo.png

# Modo de pantalla (no pantalla completa)
fullscreen = 0

# Permisos de Android
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# --- FIJAR VERSIONES DE ANDROID (SOLUCIÓN AL ERROR DE LICENCIA) ---
android.sdk = 34
android.ndk = 25b
android.build_tools_version = 34.0.0


[buildozer]

# Nivel de detalle de los mensajes
log_level = 2

# Limpiar instalación previa
clean_install = True
