# 🛠️ Sistema de Mantenimiento Preventivo

## 🎯 Objetivo
Eliminar problemas futuros mediante mantenimiento preventivo regular y automatización de tareas críticas.

---

## 🚀 Comandos Disponibles

### 1. Verificación del Sistema
```bash
python3 manage.py check_system
```
**Revisa:** Base de datos, archivos críticos, permisos, espacio en disco

### 2. Respaldo Completo
```bash
python3 manage.py backup_system
```
**Guarda:** Base de datos, archivos media, templates, configuración

### 3. Limpieza del Sistema
```bash
python3 manage.py cleanup_system
```
**Elimina:** Cache, archivos temporales, respaldos antiguos

### 4. Optimización de Base de Datos
```bash
python3 manage.py optimize_database
```
**Optimiza:** Índices, integridad, rendimiento

### 5. Reparación de Permisos
```bash
python3 manage.py fix_permissions
```
**Corrige:** Permisos de archivos y directorios

---

## 🔄 Mantenimiento Automatizado

### Script Completo
```bash
# Ejecutar todo el mantenimiento
./scripts/maintenance.sh full

# Opciones individuales
./scripts/maintenance.sh check    # Verificar
./scripts/maintenance.sh backup   # Respaldo
./scripts/maintenance.sh cleanup  # Limpiar
./scripts/maintenance.sh optimize # Optimizar
./scripts/maintenance.sh fix      # Reparar
```

### Programación (Crontab)
```bash
# Editar crontab
crontab -e

# Agregar mantenimiento semanal (domingos 2am)
0 2 * * 0 cd /ruta/al/proyecto && ./scripts/maintenance.sh full

# Mantenimiento diario (limpieza)
0 1 * * * cd /ruta/al/proyecto && ./scripts/maintenance.sh cleanup
```

---

## 📊 Monitoreo y Alertas

### Indicadores de Salud
- ✅ Base de datos accesible
- ✅ Espacio en disco > 1GB
- ✅ Permisos correctos
- ✅ Sin errores críticos
- ⚠️ Advertencias de rendimiento

### Archivos de Log
```
backups/
├── backup_20240408_120000/
│   ├── db.sqlite3
│   ├── media/
│   ├── templates/
│   └── backup_info.txt
└── backup_20240407_120000/
```

---

## 🛡️ Prevención de Problemas

### 1. Antes de Cambios
```bash
# SIEMPRE ejecutar antes de cambios importantes
./scripts/maintenance.sh full
```

### 2. Durante Desarrollo
```bash
# Verificar sistema regularmente
./scripts/maintenance.sh check

# Limpiar cache
./scripts/maintenance.sh cleanup
```

### 3. Después de Problemas
```bash
# Diagnóstico completo
./scripts/maintenance.sh check

# Restaurar último respaldo funcional
python3 manage.py restore_system backups/backup_ultimo_funcional
```

---

## 📅 Calendario Recomendado

### Diario (Automático)
- [ ] Limpieza de cache
- [ ] Verificación de espacio
- [ ] Revisión de logs

### Semanal (Domingo 2am)
- [ ] Mantenimiento completo
- [ ] Respaldo completo
- [ ] Optimización de base de datos
- [ ] Limpieza general

### Mensual (1ero del mes)
- [ ] Archivo de datos antiguos
- [ ] Revisión de permisos
- [ ] Limpieza de respaldos
- [ ] Documentación de cambios

---

## ⚠️ Solución de Problemas Comunes

### Error de Base de Datos
```bash
# Verificar integridad
python3 manage.py check_system

# Reparar permisos
python3 manage.py fix_permissions

# Optimizar
python3 manage.py optimize_database
```

### Error de Permisos
```bash
# Reparar automáticamente
python3 manage.py fix_permissions

# Verificar manualmente
ls -la db.sqlite3
```

### Sistema Lento
```bash
# Limpiar y optimizar
./scripts/maintenance.sh cleanup
./scripts/maintenance.sh optimize
```

### Espacio en Disco Lleno
```bash
# Limpiar respaldos antiguos
python3 manage.py cleanup_system

# Verificar uso de espacio
df -h
```

---

## 📞 Soporte Rápido

### Comandos Esenciales
```bash
# Verificación rápida
python3 manage.py check_system

# Mantenimiento completo
./scripts/maintenance.sh full

# Respaldo de emergencia
python3 manage.py backup_system
```

### En Caso de Emergencia
1. **Ejecutar diagnóstico:** `./scripts/maintenance.sh check`
2. **Crear respaldo:** `python3 manage.py backup_system`
3. **Reparar permisos:** `python3 manage.py fix_permissions`
4. **Documentar problema:** Fecha, hora, error, solución

---

## 🎯 Mejores Prácticas

### Prevención
- **Mantenimiento regular** (semanal recomendado)
- **Respaldos frecuentes** (diario para datos críticos)
- **Monitoreo constante** de logs y rendimiento
- **Documentación** de cambios y problemas

### Automatización
- **Programar mantenimiento** en horarios de bajo uso
- **Automatizar respaldos** y limpieza
- **Alertas automáticas** para problemas críticos
- **Rotación de respaldos** (mantiene últimos 5)

### Recuperación
- **Probar respaldos** regularmente
- **Mantener documentación** de restauración
- **Tener plan de emergencia** claro
- **Capacitación** del personal en procedimientos

---

**🏆 RESULTADO:** Sistema estable, sin problemas futuros y con mantenimiento preventivo automatizado.
