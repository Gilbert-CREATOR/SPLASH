# SPLASH POS - Sistema de Punto de Venta

Sistema de punto de venta completo y profesional desarrollado en Django con interfaz moderna y funcional.

## 🚀 Características

### 📱 Interfaz Moderna
- Diseño responsive con Bootstrap 5
- Interfaz tipo aplicación nativa
- Animaciones y transiciones suaves
- Experiencia de usuario optimizada

### 👥 Roles de Usuario
- **Administrador**: Acceso completo a dashboard, historial, productos, inventario y ganancias
- **Empleado**: Acceso exclusivo al POS para realizar ventas

### 💰 Punto de Venta (POS)
- Grid de productos con categorías
- Carrito con autoguardado (localStorage)
- Búsqueda en tiempo real
- Cálculo automático de cambio
- Validación de stock
- Métodos de pago: Efectivo, Transferencia, Tarjeta

### 📊 Dashboard Administrativo
- Estadísticas de ventas del día
- Ganancias en tiempo real
- Productos más vendidos
- Alertas de stock bajo
- Ventas recientes

### 📦 Gestión de Productos
- CRUD completo de productos
- Control de categorías
- Cálculo automático de ganancias y márgenes
- Control de stock
- Estados activo/inactivo

### 📈 Análisis de Ganancias
- Análisis detallado por producto
- Cálculo de márgenes de rentabilidad
- Filtros por período (hoy, ayer, semana, todos)
- Exportación a CSV
- Visualización de productos más rentables

### 🏪 Control de Inventario
- Movimiento automático de stock
- Registro de todos los movimientos
- Alertas de stock bajo
- Valor total del inventario
- Historial de movimientos

### 📋 Historial de Ventas
- Listado completo de ventas
- Filtros por período
- Detalle completo de cada venta
- Impresión de tickets
- Búsqueda avanzada

## 🛠️ Instalación

### Requisitos
- Python 3.8+
- PostgreSQL
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd SPLASH-POS
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Configurar base de datos PostgreSQL**
```sql
CREATE DATABASE splash_pos_db;
CREATE USER splash_pos_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE splash_pos_db TO splash_pos_user;
```

6. **Actualizar .env con la URL de la base de datos**
```
DATABASE_URL=postgresql://splash_pos_user:tu_password@localhost:5432/splash_pos_db
```

7. **Migrar la base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

8. **Crear superusuario**
```bash
python manage.py createsuperuser
```

9. **Crear productos de ejemplo (opcional)**
```bash
python manage.py shell
# Ejecutar el script de ejemplo
```

10. **Ejecutar el servidor**
```bash
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
SPLASH-POS/
├── manage.py
├── .env
├── requirements.txt
├── README.md
├── splash_pos/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── pos/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── apps.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── pos.html
│   ├── historial_ventas.html
│   ├── detalle_venta.html
│   ├── gestion_productos.html
│   ├── nuevo_producto.html
│   ├── editar_producto.html
│   ├── ganancias.html
│   └── inventario.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🎯 Uso del Sistema

### Para Administradores
1. Iniciar sesión como usuario staff
2. Acceder al dashboard para ver estadísticas
3. Gestionar productos desde el menú
4. Monitorear inventario y ganancias
5. Revisar historial de ventas

### Para Empleados
1. Iniciar sesión como usuario normal (no staff)
2. Será redirigido automáticamente al POS
3. Seleccionar productos haciendo clic
4. Procesar ventas con diferentes métodos de pago

## 🔧 Configuración

### Variables de Entorno
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True/False)
- `DATABASE_URL`: URL de conexión a PostgreSQL

### Configuración de Zona Horaria
El sistema está configurado para `America/Santo_Domingo`

### Moneda
Todos los valores se manejan en Peso Dominicano (RD$) con formato `RD$ 1,250.50`

## 📊 Modelos de Datos

### Producto
- nombre: Nombre del producto
- precio_compra: Precio de compra
- precio_venta: Precio de venta
- stock: Cantidad disponible
- categoria: Categoría del producto
- activo: Estado del producto

### Venta
- numero_venta: Número único de venta
- fecha: Fecha y hora de la venta
- total: Total de la venta
- metodo_pago: Método de pago utilizado
- dinero_recibido: Dinero recibido (para efectivo)
- cambio: Cambio devuelto
- nota: Nota adicional
- usuario: Usuario que realizó la venta

### DetalleVenta
- venta: Venta asociada
- producto: Producto vendido
- cantidad: Cantidad vendida
- precio_unitario: Precio unitario
- subtotal: Subtotal del detalle

## 🚀 Despliegue

### Para Producción
1. Configurar `DEBUG=False`
2. Configurar `ALLOWED_HOSTS`
3. Usar servidor WSGI (Gunicorn)
4. Configurar servidor web (Nginx)
5. Configurar SSL
6. Realizar backup periódicos

### Variables de Producción
```bash
DEBUG=False
SECRET_KEY=clave-segura-produccion
DATABASE_URL=postgresql://usuario:password@host:puerto/db
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

## 🤝 Contribuciones

1. Fork del proyecto
2. Crear feature branch
3. Realizar cambios
4. Enviar pull request

## 📄 Licencia

Este proyecto está bajo licencia MIT.

## 🆘 Soporte

Para reportar issues o solicitar ayuda:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

## 🔄 Actualizaciones

El sistema está diseñado para ser fácilmente actualizable:
- Las migraciones manejan cambios en la base de datos
- Los templates son modulares
- El CSS está organizado por componentes
- El JavaScript es modular y reutilizable

## 📱 Características Técnicas

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, JavaScript vanilla
- **Base de datos**: PostgreSQL
- **Autenticación**: Sistema de usuarios Django
- **Formato de moneda**: Peso Dominicano (RD$)
- **Zona horaria**: America/Santo_Domingo
- **Manejo de decimales**: Django Decimal (2 decimales)

## 🎨 Personalización

### Cambiar Colores
Editar `static/css/style.css` y modificar las variables CSS en `:root`

### Agregar Nuevas Funcionalidades
1. Crear modelos en `pos/models.py`
2. Agregar views en `pos/views.py`
3. Crear URLs en `pos/urls.py`
4. Crear templates en `templates/`
5. Agregar JavaScript en `static/js/`

### Personalizar Dashboard
Modificar `templates/dashboard.html` para agregar nuevos widgets o estadísticas

## 🔒 Seguridad

- Protección CSRF habilitada
- Validación backend obligatoria
- Roles de usuario bien definidos
- Manejo seguro de contraseñas
- Sanitización de datos de entrada
