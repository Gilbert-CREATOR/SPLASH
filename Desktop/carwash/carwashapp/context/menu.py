from django.urls import reverse

def menu_principal(request):
    return {
        'menu': [
            {'name': 'Inicio', 'url': '/#inicio'},
            {'name': 'Servicios', 'url': '/#tarifa'},
            {'name': 'Agendar cita', 'url': reverse('agendar_cita')},
            {'name': 'Cafetería', 'url': reverse('cafeteria_menu')},
            {'name': 'Contacto', 'url': '/#Contacto'},
        ]
    }


def menu_empleado(request):
    return {
        'menu_empleado': [
            {'name': 'Dashboard', 'url': reverse('dashboard')},
            {'name': 'Cafetería', 'url': reverse('cafeteria_menu')},
            {'name': 'Órdenes Activas', 'url': reverse('cafeteria_ordenes_activas')},
            {'name': 'Cerrar Sesión', 'url': reverse('logout')},
        ]
    }


def menu_admin(request):
    return {
        'menu_admin': [
            {'name': 'Inicio', 'url': reverse('inicio')},
            {'name': 'Perfil', 'url': reverse('perfil')},
            {'name': 'Empleados', 'url': reverse('admin_dashboard')},
            {'name': 'Dashboard', 'url': reverse('dashboard')},
            {'name': 'Cafetería', 'url': reverse('admin_productos')},
            {'name': 'Facturas', 'url': reverse('factura_list')},
            {'name': 'Vehículos / Agregar', 'url': reverse('vehiculos_admin')},
            {'name': 'Sesiones', 'url': reverse('admin_sesiones')},
            {'name': 'Estadísticas', 'url': reverse('admin_stats')},
            {'name': 'Historial', 'url': reverse('admin_historial')},
            {'name': 'Cerrar Sesión', 'url': reverse('logout')},
        ]
    }


def menu_superadmin(request):
    return {
        'menu_superadmin': [
            {'name': 'Inicio', 'url': reverse('inicio')},
            {'name': 'Perfil', 'url': reverse('perfil')},
            {'name': 'Empleados', 'url': reverse('admin_dashboard')},
            {'name': 'Dashboard', 'url': reverse('dashboard')},
            {'name': 'Cafetería', 'url': reverse('admin_productos')},
            {'name': 'Facturas', 'url': reverse('factura_list')},
            {'name': 'Vehículos / Agregar', 'url': reverse('vehiculos_admin')},
            {'name': 'Sesiones', 'url': reverse('admin_sesiones')},
            {'name': 'Estadísticas', 'url': reverse('admin_stats')},
            {'name': 'Historial', 'url': reverse('admin_historial')},
            {'name': 'Cerrar Sesión', 'url': reverse('logout')},
        ]
    }