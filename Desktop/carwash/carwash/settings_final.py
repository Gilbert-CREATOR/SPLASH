"""
CONFIGURACIÓN FINAL - B&B CAR WASH
Añade estas configuraciones a tu archivo carwash/settings.py
"""

# ===================================
# EMAIL CONFIGURATION
# ===================================

# Gmail (Recomendado para desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'  # CAMBIAR POR TU EMAIL
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'  # CAMBIAR POR TU CONTRASEÑA DE APP
DEFAULT_FROM_EMAIL = 'B&B Car Wash <tu_email@gmail.com>'

# Para pruebas sin enviar emails reales:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===================================
# SMS CONFIGURATION (TWILIO)
# ===================================

# Obtén estos datos de https://www.twilio.com/console
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # CAMBIAR
TWILIO_AUTH_TOKEN = 'your_auth_token_here'              # CAMBIAR
TWILIO_PHONE_NUMBER = '+18091234567'                  # CAMBIAR POR TU NÚMERO

# ===================================
# CELERY CONFIGURATION
# ===================================

import os
from celery import Celery

# Redis Configuration
REDIS_URL = 'redis://localhost:6379/0'

# Celery Settings
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santo_Domingo'
CELERY_ENABLE_UTC = True

# Colas para diferentes tipos de tareas
CELERY_TASK_ROUTES = {
    'carwashapp.tasks.enviar_notificacion_cita_confirmada': {'queue': 'notifications'},
    'carwashapp.tasks.enviar_notificacion_cita_recordatorio': {'queue': 'notifications'},
    'carwashapp.tasks.enviar_notificacion_orden_lista': {'queue': 'notifications'},
    'carwashapp.tasks.enviar_notificacion_factura_generada': {'queue': 'notifications'},
    'carwashapp.tasks.enviar_recordatorios_citas': {'queue': 'notifications'},
    'carwashapp.tasks.verificar_stock_bajo': {'queue': 'notifications'},
    'carwashapp.tasks.enviar_reporte_diario': {'queue': 'reports'},
    'carwashapp.tasks.actualizar_estadisticas_diarias': {'queue': 'analytics'},
    'carwashapp.tasks.verificar_citas_vencidas': {'queue': 'maintenance'},
    'carwashapp.tasks.limpiar_notificaciones_antiguas': {'queue': 'maintenance'},
}

# ===================================
# CELERY BEAT SCHEDULE
# ===================================

CELERY_BEAT_SCHEDULE = {
    # Recordatorios de citas (todos los días a las 8:00 AM)
    'enviar-recordatorios-citas': {
        'task': 'carwashapp.tasks.enviar_recordatorios_citas',
        'schedule': 60.0 * 60.0 * 24.0,  # Cada 24 horas
        'options': {'queue': 'notifications'}
    },
    
    # Verificación de stock bajo (cada 2 horas)
    'verificar-stock-bajo': {
        'task': 'carwashapp.tasks.verificar_stock_bajo',
        'schedule': 60.0 * 60.0 * 2.0,  # Cada 2 horas
        'options': {'queue': 'notifications'}
    },
    
    # Reporte diario (todos los días a las 6:00 PM)
    'enviar-reporte-diario': {
        'task': 'carwashapp.tasks.enviar_reporte_diario',
        'schedule': 60.0 * 60.0 * 24.0,  # Cada 24 horas
        'options': {'queue': 'reports'}
    },
    
    # Verificar citas vencidas (cada hora)
    'verificar-citas-vencidas': {
        'task': 'carwashapp.tasks.verificar_citas_vencidas',
        'schedule': 60.0 * 60.0,  # Cada hora
        'options': {'queue': 'maintenance'}
    },
    
    # Actualizar estadísticas (cada noche a medianoche)
    'actualizar-estadisticas-diarias': {
        'task': 'carwashapp.tasks.actualizar_estadisticas_diarias',
        'schedule': 60.0 * 60.0 * 24.0,  # Cada 24 horas
        'options': {'queue': 'analytics'}
    },
    
    # Limpiar notificaciones antiguas (una vez por semana)
    'limpiar-notificaciones-antiguas': {
        'task': 'carwashapp.tasks.limpiar_notificaciones_antiguas',
        'schedule': 60.0 * 60.0 * 24.0 * 7.0,  # Cada 7 días
        'options': {'queue': 'maintenance'}
    },
}

# ===================================
# DJANGO-CELERY-BEAT
# ===================================

INSTALLED_APPS += [
    'django_celery_beat',
    'django_celery_results',
]

# Database para Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ===================================
# NOTIFICATION SETTINGS
# ===================================

NOTIFICATION_SETTINGS = {
    'EMAIL_ENABLED': True,
    'SMS_ENABLED': True,
    'RECORDATORIO_HORAS_ANTES': 24,
    'STOCK_BAJO_UMBRAL': 5,
    'STOCK_CRITICO_UMBRAL': 2,
    'ADMIN_EMAILS': ['admin@bbcarwash.com'],
}

# ===================================
# LOGGING CONFIGURATION
# ===================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/carwash.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'carwashapp': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ===================================
# TIMEZONE CONFIGURATION
# ===================================

TIME_ZONE = 'America/Santo_Domingo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ===================================
# MEDIA FILES
# ===================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===================================
# STATIC FILES
# ===================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ===================================
# SECURITY SETTINGS
# ===================================

# Para desarrollo
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Para producción (cambiar cuando sea necesario)
# DEBUG = False
# ALLOWED_HOSTS = ['tudominio.com']
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
