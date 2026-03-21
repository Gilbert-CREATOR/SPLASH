"""
CONFIGURACIÓN DE SMS - B&B CAR WASH
Instrucciones paso a paso para configurar Twilio SMS
"""

# ===================================
# PASO 1: Crear cuenta en Twilio
# ===================================

# 1. Regístrate en https://www.twilio.com/
# 2. Verifica tu email y número de teléfono
# 3. Obtén tu Account SID y Auth Token del Dashboard

# ===================================
# PASO 2: Obtener un número de teléfono
# ===================================

# 1. Ve a Phone Numbers > Buy a Number
# 2. Selecciona Dominican Republic (+1 809/829/849)
# 3. Busca números disponibles
# 4. Compra un número (cuesta ~$1 USD al mes)

# ===================================
# PASO 3: Configurar en settings.py
# ===================================

TWILIO_CONFIG = {
    'TWILIO_ACCOUNT_SID': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  # Tu Account SID
    'TWILIO_AUTH_TOKEN': 'your_auth_token_here',              # Tu Auth Token
    'TWILIO_PHONE_NUMBER': '+18091234567',                  # Tu número de Twilio
}

# Copia esto en carwash/settings.py:
"""
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'your_auth_token_here'
TWILIO_PHONE_NUMBER = '+18091234567'
"""

# ===================================
# PASO 4: Instalar Twilio Python
# ===================================

# Ejecuta en terminal:
"""
pip install twilio
"""

# ===================================
# PASO 5: Script de prueba SMS
# ===================================

TEST_SMS_SCRIPT = """
# test_sms.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')
django.setup()

from twilio.rest import Client
from django.conf import settings

# Tu Account SID y Auth Token
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

try:
    message = client.messages.create(
        body='🚗 B&B Car Wash: Prueba de SMS! Si recibes esto, la configuración es correcta.',
        from_=settings.TWILIO_PHONE_NUMBER,
        to='+18091234567'  # Tu número de teléfono (formato internacional)
    )
    print(f"✅ SMS enviado! SID: {message.sid}")
except Exception as e:
    print(f"❌ Error enviando SMS: {e}")
"""

# Ejecuta con: python test_sms.py

# ===================================
# PASO 6: Actualizar servicio de notificaciones
# ===================================

# Actualiza carwashapp/services/notifications.py con:
"""
from twilio.rest import Client
from django.conf import settings

class SMSService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_sms(self, to_phone, message):
        try:
            # Limpiar número de teléfono
            phone = self._clean_phone_number(to_phone)
            
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone
            )
            
            logger.info(f"SMS enviado exitosamente a {phone}. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando SMS a {to_phone}: {str(e)}")
            return False
"""

# ===================================
# COSTOS DE TWILIO
# ===================================

"""
COSTOS APROXIMADOS (República Dominicana):
- Número de teléfono: $1 USD/mes
- SMS saliente: ~$0.05 USD por mensaje
- SMS entrante: Gratis

EJEMPLO MENSUAL:
- 1 número: $1.00
- 100 SMS: $5.00
- Total mensual: ~$6.00
"""

# ===================================
# ALTERNATIVAS MÁS ECONÓMICAS
# ===================================

"""
OPCIÓN 1: Textlocal (más económico)
- Costo: ~$0.04 USD por SMS a RD
- No requiere número mensual
- Configuración más simple

OPCIÓN 2: Vonage (Nexmo)
- Costo: ~$0.03 USD por SMS a RD
- Primer número gratis
- API REST simple

OPCIÓN 3: Email-to-SMS (gratis)
- Usa gateways de email a SMS
- Limitaciones de operador
- Menos confiable
"""
