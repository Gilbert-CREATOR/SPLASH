# 🛠️ SPLASH POS - Guía de Mantenimiento y Prevención de Problemas

## 📋 Índice
1. [Comandos de Mantenimiento](#comandos-de-mantenimiento)
2. [Verificación del Sistema](#verificación-del-sistema)
3. [Respaldo y Restauración](#respaldo-y-restauración)
4. [Limpieza del Sistema](#limpieza-del-sistema)
5. [Permisos de Archivos](#permisos-de-archivos)
6. [Problemas Comunes](#problemas-comunes)
7. [Mejores Prácticas](#mejores-prácticas)

---

## 🚀 Comandos de Mantenimiento

### Verificación del Sistema
```bash
python3 manage.py check_system
```
**Qué hace:** Revisa la salud general del sistema, archivos críticos y configuración.

### Respaldo Completo
```bash
python3 manage.py backup_system
```
**Qué hace:** Crea un respaldo completo de base de datos, archivos y configuración.

### Limpieza del Sistema
```bash
python3 manage.py cleanup_system
```
**Qué hace:** Elimina archivos temporales, cache y respaldos antiguos.

### Reparación de Permisos
```bash
python3 manage.py fix_permissions
```
**Qué hace:** Corrige permisos de archivos y directorios críticos.

---

## 🔍 Verificación del Sistema

### Diagnóstico Automático
El comando `check_system` verifica:

- ✅ **Base de datos:** Existencia y tamaño
- ✅ **Directorios críticos:** media/, templates/, pos/
- ✅ **Versiones:** Python y Django
- ✅ **Archivos clave:** manage.py, requirements.txt
- ✅ **Espacio en disco:** Disponibilidad
- ⚠️ **Advertencias:** Problemas potenciales

### Solución de Problemas
Si `check_system` detecta problemas:

1. **Base de datos no encontrada:**
   ```bash
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```

2. **Directorios faltantes:**
   ```bash
   mkdir -p media templates static
   ```

3. **Permisos incorrectos:**
   ```bash
   python3 manage.py fix_permissions
   ```

---

## 💾 Respaldo y Restauración

### Respaldo Automático
```bash
# Crear respaldo con timestamp
python3 manage.py backup_system

# Ver respaldos existentes
ls -la backups/
```

**El respaldo incluye:**
- 📊 Base de datos (db.sqlite3)
- 📁 Archivos media (imágenes, documentos)
- 📄 Templates del sistema
- 🐍 Aplicación POS completa

### Restauración del Sistema
```bash
# Restaurar desde un respaldo específico
python3 manage.py restore_system backups/backup_20240408_120000

# Confirmación requerida
⚠️ This will overwrite current system. Are you sure? (yes/no):
```

### Programación de Respaldos
Recomendación: Respaldar diariamente o semanalmente

```bash
# Agregar a crontab (Linux/Mac)
0 2 * * * cd /ruta/al/proyecto && python3 manage.py backup_system
```

---

## 🧹 Limpieza del Sistema

### Limpieza Automática
```bash
python3 manage.py cleanup_system
```

**Qué limpia:**
- 🗑️ Archivos Python cache (__pycache__)
- 🗑️ Archivos compilados (.pyc, .pyo)
- 🗑️ Respaldos antiguos (mantiene últimos 5)
- 🗑️ Archivos temporales (.tmp, .temp)
- 🗑️ Logs grandes (>10MB)

### Limpieza Manual
```bash
# Limpiar cache de Django
python3 manage.py clear_cache

# Limpiar sesiones
python3 manage.py clearsessions

# Recolectar archivos estáticos
python3 manage.py collectstatic --noinput
```

---

## 🔐 Permisos de Archivos

### Permisos Correctos
```bash
# Base de datos - lectura/escritura solo para owner
chmod 600 db.sqlite3

# Directorios - lectura/escritura/ejecución
chmod 755 media templates static

# Scripts - ejecutable para owner
chmod 700 manage.py
```

### Reparación Automática
```bash
python3 manage.py fix_permissions
```

### Verificación de Permisos
```bash
# Ver permisos actuales
ls -la

# Ver problemas de permisos
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
```

---

## ⚠️ Problemas Comunes y Soluciones

### 1. Error de Base de Datos
**Problema:** `django.db.utils.OperationalError: unable to open database file`

**Solución:**
```bash
# Verificar permisos
ls -la db.sqlite3

# Reparar permisos
python3 manage.py fix_permissions

# Verificar integridad
sqlite3 db.sqlite3 "PRAGMA integrity_check;"
```

### 2. Error de Migraciones
**Problema:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solución:**
```bash
# Respaldar primero
python3 manage.py backup_system

# Resetear migraciones
python3 manage.py migrate --fake-initial
python3 manage.py migrate --fake
```

### 3. Error de Permisos
**Problema:** `Permission denied` al acceder archivos

**Solución:**
```bash
# Reparar permisos automáticamente
python3 manage.py fix_permissions

# Manualmente
sudo chown -R $USER:$USER .
chmod -R 755 .
chmod 600 db.sqlite3
```

### 4. Error de Servidor
**Problema:** `That port is already in use`

**Solución:**
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>

# Usar otro puerto
python3 manage.py runserver 8001
```

### 5. Error de Memoria
**Problema:** Sistema lento o sin respuesta

**Solución:**
```bash
# Limpiar sistema
python3 manage.py cleanup_system

# Reiniciar servidor
python3 manage.py runserver

# Ver uso de memoria
python3 manage.py check_system
```

---

## 📅 Calendario de Mantenimiento

### Diario
- [ ] Verificar espacio en disco
- [ ] Revisar logs de errores
- [ ] Respaldar si hay cambios importantes

### Semanal
- [ ] Ejecutar `check_system` completo
- [ ] Limpiar cache y archivos temporales
- [ ] Respaldar sistema completo
- [ ] Verificar actualizaciones de seguridad

### Mensual
- [ ] Revisar y optimizar base de datos
- [ ] Limpiar respaldos antiguos
- [ ] Verificar permisos del sistema
- [ ] Documentar cambios realizados

---

## 🛡️ Mejores Prácticas

### Antes de Cambios Importantes
1. **SIEMPRE** crear respaldo:
   ```bash
   python3 manage.py backup_system
   ```

2. **VERIFICAR** sistema:
   ```bash
   python3 manage.py check_system
   ```

3. **DOCUMENTAR** cambios realizados

### Durante Desarrollo
1. **LIMPIAR** cache regularmente
2. **MONITOREAR** logs de errores
3. **EVITAR** cambios en producción sin pruebas

### Después de Problemas
1. **IDENTIFICAR** causa raíz
2. **DOCUMENTAR** solución aplicada
3. **IMPLEMENTAR** medidas preventivas
4. **VERIFICAR** sistema completamente

---

## 🆘️ Ayuda Rápida

### Comandos Esenciales
```bash
# Verificar sistema
python3 manage.py check_system

# Respaldar
python3 manage.py backup_system

# Limpiar
python3 manage.py cleanup_system

# Reparar permisos
python3 manage.py fix_permissions
```

### En Caso de Emergencia
1. **PARAR** servidor
2. **RESPALDAR** sistema actual
3. **DIAGNOSTICAR** con `check_system`
4. **RESTAURAR** último respaldo funcional
5. **CONTACTAR** soporte técnico

---

## 📞 Soporte y Contacto

### Documentación Adicional
- 📖 [Django Documentation](https://docs.djangoproject.com/)
- 🔧 [Python Documentation](https://docs.python.org/3/)

### Registro de Problemas
Mantener un registro de:
- Fecha y hora del problema
- Mensaje de error exacto
- Pasos para reproducir
- Solución aplicada
- Medidas preventivas

---

**🎯 CONSEJO FINAL:** Un sistema bien mantenido es un sistema estable. Realiza mantenimientos preventivos regularmente y mantén respaldos actualizados.
