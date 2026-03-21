#!/bin/bash

echo "🚀 INICIANDO SERVICIOS - B&B CAR WASH"
echo "=================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar Redis
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis no está instalado. Ejecuta: brew install redis"
    exit 1
fi

# Iniciar Redis
echo "🔴 Iniciando Redis..."
redis-server --daemonize yes
sleep 2

# Verificar Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis iniciado correctamente"
else
    echo "❌ Error iniciando Redis"
    exit 1
fi

# Migrar base de datos
echo "💾 Migrando base de datos..."
python3 manage.py migrate

# Iniciar Celery Worker
echo "🔄 Iniciando Celery Worker..."
celery -A carwash worker -l info --detach
sleep 2

# Iniciar Celery Beat
echo "⏰ Iniciando Celery Beat..."
celery -A carwash beat -l info --detach
sleep 2

# Verificar Celery
if celery -A carwash inspect active > /dev/null 2>&1; then
    echo "✅ Celery iniciado correctamente"
else
    echo "❌ Error iniciando Celery"
fi

# Iniciar Django Development Server
echo "🌐 Iniciando Django Server..."
echo "📊 Dashboard avanzado: http://127.0.0.1:8000/dashboard/avanzado/"
echo "📧 Prueba de notificaciones: python3 test_notifications.py"
echo "🌸 Flower (monitoreo): celery -A carwash flower"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"

# Trap para detener servicios al salir
trap 'echo "🛑 Deteniendo servicios..."; pkill -f celery; redis-cli shutdown; exit' INT

python3 manage.py runserver
