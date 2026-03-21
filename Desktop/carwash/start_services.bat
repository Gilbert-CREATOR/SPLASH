@echo off
echo 🚀 INICIANDO SERVICIOS - B&B CAR WASH
echo ==================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    pause
    exit /b 1
)

REM Verificar Redis
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis no está instalado
    echo Descarga Redis para Windows desde: https://github.com/microsoftarchive/redis/releases
    pause
    exit /b 1
)

REM Iniciar Redis
echo 🔴 Iniciando Redis...
start /B redis-server
timeout /t 3 /nobreak >nul

REM Verificar Redis
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Error iniciando Redis
    pause
    exit /b 1
)
echo ✅ Redis iniciado correctamente

REM Migrar base de datos
echo 💾 Migrando base de datos...
python manage.py migrate

REM Iniciar Celery Worker
echo 🔄 Iniciando Celery Worker...
start /B celery -A carwash worker -l info
timeout /t 2 /nobreak >nul

REM Iniciar Celery Beat
echo ⏰ Iniciando Celery Beat...
start /B celery -A carwash beat -l info
timeout /t 2 /nobreak >nul

REM Iniciar Django Development Server
echo 🌐 Iniciando Django Server...
echo 📊 Dashboard avanzado: http://127.0.0.1:8000/dashboard/avanzado/
echo 📧 Prueba de notificaciones: python test_notifications.py
echo 🌸 Flower (monitoreo): celery -A carwash flower
echo.
echo Presiona Ctrl+C para detener el servidor

python manage.py runserver

pause
