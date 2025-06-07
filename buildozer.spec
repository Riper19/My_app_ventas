# --- ESTE ES EL ARCHIVO buildozer.spec COMPLETO Y CORREGIDO ---

[app]

# (Obligatorio) Título de tu aplicación, el que aparecerá bajo el ícono.
title = Mi Inventario

# (Obligatorio) Nombre del paquete. TODO EN MINÚSCULAS Y SIN ESPACIOS.
package.name = miinventario

# (Obligatorio) Dominio del paquete. Puedes inventarlo.
package.domain = org.test

# (Obligatorio) Directorio donde está tu código. El punto '.' significa "esta carpeta".
source.dir = .

# (Obligatorio) Extensiones de archivo que se incluirán.
# Asegúrate de que estén todas las que usas: py, kv, png, gif, json.
source.include_exts = py,png,jpg,jpeg,gif,json,kv

# (Obligatorio) La versión de tu app.
version = 1.0

# (Obligatorio) Librerías que tu app necesita. Kivy ya está.
requirements = python3,kivy

# Orientación de la pantalla. Tu app parece vertical.
orientation = portrait

# (Opcional) El ícono de tu aplicación (un archivo .png de tu proyecto).
# Asegúrate de que el nombre del archivo exista en tu carpeta.
icon.filename = %(source.dir)s/icon.png

# (Opcional) La imagen que aparece mientras carga la app (splash screen).
presplash.filename = %(source.dir)s/fondo.png

# (Opcional) Para que no sea a pantalla completa y se vean las barras de Android.
fullscreen = 0

# --- ¡MUY IMPORTANTE! PERMISOS DE ANDROID ---
# Tu app necesita leer archivos con el FileChooser.
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# --- ¡IMPORTANTE! FIJAR VERSIONES DE ANDROID (SOLUCIÓN AL ERROR DE LICENCIA) ---
# Le decimos a Buildozer qué versiones estables y conocidas usar.
android.sdk = 34
android.ndk = 25b
android.build_tools_version = 34.0.0


[buildozer]

# Nivel de detalle de los mensajes de error. No es necesario cambiarlo.
log_level = 2

# Permite que Buildozer borre la carpeta de compilación si es necesario.
clean_install = True
