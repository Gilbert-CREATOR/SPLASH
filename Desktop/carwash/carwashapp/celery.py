"""
Configuración de Celery - B&B Car Wash
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')

app = Celery('carwash')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configuración de tareas programadas
app.conf.beat_schedule = {
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

# Configuración de colas
app.conf.task_routes = {
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

# Configuración de worker
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_max_tasks_per_child = 50

# Configuración de tiempo de espera
app.conf.task_soft_time_limit = 300  # 5 minutos
app.conf.task_time_limit = 600       # 10 minutos

# Configuración de reintentos
app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/m',  # Máximo 10 tareas por minuto
        'time_limit': 300,     # 5 minutos límite
    },
    'carwashapp.tasks.enviar_notificacion_cita_confirmada': {
        'rate_limit': '20/m',  # Más alto para confirmaciones inmediatas
        'time_limit': 60,      # 1 minuto límite
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
