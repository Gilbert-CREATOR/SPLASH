"""
Configuración de Notificaciones - B&B Car Wash
"""

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Cambiar según tu proveedor
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@bbcarwash.com'  # Cambiar por tu email
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'  # Usar contraseña de aplicación
DEFAULT_FROM_EMAIL = 'B&B Car Wash <noreply@bbcarwash.com>'

# SMS Settings (Ejemplo con Twilio)
SMS_API_KEY = 'tu_api_key_twilio'
SMS_API_URL = 'https://api.twilio.com/2010-04-01/Accounts/'
SMS_FROM_NUMBER = '+18091234567'  # Número de Twilio

# Configuración de notificaciones
NOTIFICATION_SETTINGS = {
    'EMAIL_ENABLED': True,
    'SMS_ENABLED': True,
    'RECORDATORIO_HORAS_ANTES': 24,
    'STOCK_BAJO_UMBRAL': 5,
    'STOCK_CRITICO_UMBRAL': 2,
    'ADMIN_EMAILS': ['admin@bbcarwash.com', 'gerente@bbcarwash.com'],
}

# Templates de notificaciones
EMAIL_TEMPLATES = {
    'cita_confirmacion': 'emails/cita_confirmacion.html',
    'cita_recordatorio': 'emails/cita_recordatorio.html',
    'cita_cancelacion': 'emails/cita_cancelacion.html',
    'orden_lista': 'emails/orden_lista.html',
    'factura_generada': 'emails/factura_generada.html',
    'stock_bajo_alerta': 'emails/stock_bajo_alerta.html',
    'reporte_diario': 'emails/reporte_diario.html',
}

# Mensajes SMS predefinidos
SMS_TEMPLATES = {
    'cita_confirmacion': 'B&B Car Wash: Tu cita para {servicio} el {fecha} a las {hora} ha sido confirmada. ¡Te esperamos! 🚗',
    'cita_recordatorio': 'B&B Car Wash: Recordatorio! Tu cita mañana a las {hora} para {servicio}. ¡No faltes! ⏰',
    'cita_cancelacion': 'B&B Car Wash: Tu cita del {fecha} a las {hora} ha sido cancelada. Llámanos si necesitas reagendar. 📞',
    'orden_lista': 'B&B Car Wash: ¡Tu orden de cafetería está lista! Pásala a recoger. Total: ${total} ☕',
    'factura_generada': 'B&B Car Wash: Se ha generado tu factura #{numero} por ${total}. Gracias por tu preferencia! 💰',
    'stock_bajo': 'B&B Car Wash: ¡Alerta! El producto {producto} tiene solo {stock} unidades disponibles. 🚨',
}

# Horarios de envío de notificaciones
NOTIFICATION_SCHEDULE = {
    'RECORDATORIOS_DIARIOS': '08:00',  # 8:00 AM
    'REPORTE_DIARIO': '18:00',        # 6:00 PM
    'VERIFICACION_STOCK': '10:00',    # 10:00 AM
    'NO_ENVIAR_HORAS': ['22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00'],
}
