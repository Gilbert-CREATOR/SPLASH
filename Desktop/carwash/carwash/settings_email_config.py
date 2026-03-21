"""
CONFIGURACIÓN DE EMAIL - B&B CAR WASH
Instrucciones paso a paso para configurar el servicio de email
"""

# ===================================
# OPCIÓN 1: GMAIL (Recomendado para desarrollo)
# ===================================

# PASO 1: Habilitar 2FA en tu cuenta Gmail
# - Ve a https://myaccount.google.com/security
# - Activa "Verificación en dos pasos"

# PASO 2: Generar Contraseña de Aplicación
# - Ve a https://myaccount.google.com/apppasswords
# - Selecciona "Otra (nombre personalizado)"
# - Escribe: "B&B Car Wash"
# - Copia la contraseña generada (16 caracteres)

# PASO 3: Configurar en settings.py
EMAIL_SETTINGS_GMAIL = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'tu_email@gmail.com',  # Cambiar por tu email
    'EMAIL_HOST_PASSWORD': 'tu_contraseña_de_app',  # Contraseña de 16 caracteres
    'DEFAULT_FROM_EMAIL': 'B&B Car Wash <tu_email@gmail.com>',
}

# ===================================
# OPCIÓN 2: OUTLOOK/HOTMAIL
# ===================================

# PASO 1: Habilitar 2FA en tu cuenta Outlook
# - Ve a https://account.live.com/proofs/manage
# - Activa la verificación en dos pasos

# PASO 2: Generar Contraseña de Aplicación
# - Ve a https://account.live.com/passwords
# - Crea una nueva contraseña de aplicación
# - Nombre: "B&B Car Wash"
# - Copia la contraseña generada

# PASO 3: Configurar en settings.py
EMAIL_SETTINGS_OUTLOOK = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp-mail.outlook.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'tu_email@outlook.com',
    'EMAIL_HOST_PASSWORD': 'tu_contraseña_de_app',
    'DEFAULT_FROM_EMAIL': 'B&B Car Wash <tu_email@outlook.com>',
}

# ===================================
# OPCIÓN 3: SENDGRID (Recomendado para producción)
# ===================================

# PASO 1: Crear cuenta en SendGrid
# - Regístrate en https://sendgrid.com/
# - Verifica tu email

# PASO 2: Crear API Key
# - Ve a Settings > API Keys
# - Crea nueva API Key
# - Selecciona "Restricted Access"
# - Permisos: Mail Send > Full Access
# - Copia la API Key

# PASO 3: Configurar en settings.py
EMAIL_SETTINGS_SENDGRID = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.sendgrid.net',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'apikey',
    'EMAIL_HOST_PASSWORD': 'tu_api_key_de_sendgrid',
    'DEFAULT_FROM_EMAIL': 'B&B Car Wash <noreply@bbcarwash.com>',
}

# ===================================
# PASO 4: Añadir a settings.py principal
# ===================================

# Copia y pega esto en tu archivo carwash/settings.py:

"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Cambiar según tu proveedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'  # Tu email
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'  # Contraseña de aplicación
DEFAULT_FROM_EMAIL = 'B&B Car Wash <tu_email@gmail.com>'

# Para pruebas en desarrollo (sin enviar emails reales)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
"""

# ===================================
# PASO 5: Probar configuración
# ===================================

# Crea este script de prueba:
TEST_EMAIL_SCRIPT = """
# test_email.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")

try:
    send_mail(
        'Prueba de Email - B&B Car Wash',
        'Este es un email de prueba para verificar que la configuración funciona correctamente.',
        settings.DEFAULT_FROM_EMAIL,
        ['tu_email_destino@gmail.com'],  # Cambiar por tu email
        fail_silently=False,
    )
    print("✅ Email enviado exitosamente!")
except Exception as e:
    print(f"❌ Error enviando email: {e}")
"""

# Ejecuta con: python test_email.py
