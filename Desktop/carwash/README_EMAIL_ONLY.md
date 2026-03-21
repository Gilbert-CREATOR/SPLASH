# 📧 Sistema de Notificaciones (Solo Email) - B&B Car Wash

Guía simplificada del sistema de notificaciones automáticas usando solo emails.

## 🚀 Instalación Rápida

### 1. Instalar Dependencias
```bash
pip install celery redis django-celery-beat django-celery-results
```

### 2. Instalar Redis
```bash
# Mac
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Docker (recomendado)
docker run -d -p 6379:6379 --name redis redis:alpine
```

### 3. Configurar Email
1. **Habilita 2FA en tu Gmail**
2. **Genera contraseña de aplicación**: https://myaccount.google.com/apppasswords
3. **Añade a settings.py**:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'
DEFAULT_FROM_EMAIL = 'B&B Car Wash <tu_email@gmail.com>'
```

### 4. Configurar Celery
1. **Añade a carwash/__init__.py**:
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

2. **Añade a settings.py** (ver `settings_email_only.py`)

3. **Migra la base de datos**:
```bash
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```

### 5. Iniciar Servicios
```bash
# Mac/Linux
chmod +x start_services.sh
./start_services.sh

# Windows
start_services.bat
```

## 🧪 Probar el Sistema

### Ejecutar Pruebas Completas
```bash
python test_email_only.py
```

### Pruebas Individuales
```bash
# Probar email
python -c "
from django.core.mail import send_mail
send_mail('Test', 'Mensaje', 'tu_email@gmail.com', ['destino@gmail.com'])
"

# Probar Celery
celery -A carwash call carwashapp.tasks.enviar_recordatorios_citas
```

## 📊 Dashboard Avanzado

Accede al dashboard con métricas en tiempo real:
- **URL**: http://127.0.0.1:8000/dashboard/avanzado/
- **Reportes**: http://127.0.0.1:8000/dashboard/reportes/

## 🔧 Comandos Útiles

### Celery
```bash
# Ver workers activos
celery -A carwash inspect active

# Ver tareas programadas
celery -A carwash beat schedule

# Ver estadísticas
celery -A carwash stats

# Iniciar con logs
celery -A carwash worker -l info

# Iniciar beat scheduler
celery -A carwash beat -l info
```

### Redis
```bash
# Verificar conexión
redis-cli ping

# Ver keys
redis-cli keys "*"

# Limpiar todo
redis-cli flushall
```

### Monitoreo
```bash
# Flower (interfaz web)
pip install flower
celery -A carwash flower
# Visita: http://localhost:5555
```

## 📧 Tipos de Notificaciones (Email)

### 1. ✅ Confirmación de Cita
- **Email**: Template HTML profesional
- **Disparador**: Al agendar cita

### 2. ⏰ Recordatorio de Cita
- **Email**: 24 horas antes
- **Disparador**: Tarea programada

### 3. 🚨 Alertas de Stock
- **Email**: A administradores
- **Umbral**: ≤5 unidades (bajo), ≤2 (crítico)
- **Disparador**: Cada 2 horas

### 4. 🧾 Factura Generada
- **Email**: Con detalles de factura
- **Disparador**: Al crear factura

## 🔄 Tareas Programadas

| Tarea | Frecuencia | Descripción |
|------|------------|-------------|
| Recordatorios de citas | Diario (8 AM) | Enviar recordatorios 24h antes |
| Verificación de stock | Cada 2 horas | Alertar stock bajo |
| Reporte diario | Diario (6 PM) | Enviar estadísticas a admin |
| Citas vencidas | Cada hora | Cancelar citas pasadas |
| Estadísticas | Diario (medianoche) | Actualizar métricas |
| Limpieza | Semanal | Eliminar logs antiguos |

## 🛠️ Troubleshooting

### Email no funciona
```bash
# Verificar configuración
python -c "from django.conf import settings; print(settings.EMAIL_BACKEND)"

# Probar conexión
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('tu_email@gmail.com', 'tu_contraseña')
print('✅ Conexión exitosa')
"
```

### Celery no inicia
```bash
# Verificar Redis
redis-cli ping

# Verificar importación
python -c "from carwashapp.tasks import enviar_recordatorios_citas"

# Iniciar con debug
celery -A carwash worker -l debug
```

## 💰 Costos

### Email
- **Gmail/Outlook**: Gratis
- **SendGrid**: $0.10 USD por 1000 emails

### Redis
- **Auto-hospedado**: Gratis
- **Redis Cloud**: $5 USD/mes (básico)

## 🚀 Para Producción

### 1. Seguridad
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com']
SECURE_SSL_REDIRECT = True
```

### 2. Performance
```python
# Múltiples workers
celery -A carwash worker -c 4

# Configuración de producción
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
```

### 3. Monitoreo
```bash
# Con supervisor
sudo apt install supervisor

# Configurar /etc/supervisor/conf.d/celery.conf
[program:celery_worker]
command=celery -A carwash worker -l info
directory=/path/to/your/project
user=www-data
autostart=true
autorestart=true
```

## 📞 Soporte

Si tienes problemas:
1. **Revisa los logs**: `logs/carwash.log`
2. **Ejecuta pruebas**: `python test_email_only.py`
3. **Verifica configuración**: Compara con `settings_email_only.py`
4. **Reinicia servicios**: `./start_services.sh`

---

## 🎉 Ventajas del Sistema de Email

### ✅ Beneficios
- **Costo cero** con Gmail/Outlook
- **Alta deliverability** con SMTP profesional
- **Templates HTML** profesionales
- **Tareas programadas** automáticas
- **Logs completos** de envíos
- **Dashboard avanzado** con métricas

### 📈 Funcionalidades
- **Confirmación automática** de citas
- **Recordatorios inteligentes** 24h antes
- **Alertas de stock** para administradores
- **Reportes diarios** de operaciones
- **Integración completa** con el sistema

### 🎯 Características Técnicas
- **Asíncrono** con Celery
- **Persistencia** con Redis
- **Reintentos automáticos**
- **Logging detallado**
- **Monitoreo** con Flower

---

**🎉 ¡Felicidades! Tu sistema de notificaciones por email está listo para usar.**
