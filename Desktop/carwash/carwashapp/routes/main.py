from django.urls import path
from carwashapp.views import inicio, zonadeservicio, sobrenosotros, agendar_cita
from carwashapp.views import login_view, logout_view, registro
from carwashapp.views import dashboard, dashboard_citas, dashboard_cita_detalle, eliminar_cita, cambiar_estado_cita, empleado_vehiculos
from carwashapp.views import admin_dashboard, admin_stats, admin_historial, admin_sesiones
from carwashapp.views import perfil
from carwashapp.views import vehiculos_admin, vehiculo_editar_marca, vehiculo_editar_modelo
from carwashapp.views import cafeteria_menu, cafeteria_orden_create, cafeteria_orden_detalle, cafeteria_ordenes_activas, cafeteria_cambiar_estado
from carwashapp.views import factura_crear, factura_detalle, factura_pagar, factura_list
from carwashapp.views import admin_categorias, admin_categoria_create, admin_categoria_edit, admin_categoria_toggle, admin_categoria_delete
from carwashapp.views import admin_productos, admin_producto_create, admin_producto_edit, admin_producto_toggle, admin_producto_delete
from carwashapp.views import admin_sesion_finalizar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==========================
    # Rutas Principales
    # ==========================
    path('', inicio, name='inicio'),
    path('nosotros/', sobrenosotros, name='nosotros'),
    path('servicios/', zonadeservicio, name='servicios'),
    
    # ==========================
    # Autenticación
    # ==========================
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),

    # ==========================
    # Dashboard
    # ==========================
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/citas/', dashboard_citas, name='dashboard_citas'),
    path('dashboard/cita/<int:id>/', dashboard_cita_detalle, name='dashboard_cita_detalle'),
    path('dashboard/cita/<int:id>/eliminar/', eliminar_cita, name='eliminar_cita'),
    path('dashboard/cita/<int:id>/estado/<str:nuevo_estado>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    path('dashboard/vehiculos/', empleado_vehiculos, name='empleado_vehiculos'),

    # ==========================
    # Citas
    # ==========================
    path('agendar-cita/', agendar_cita, name='agendar_cita'),

    # ==========================
    # Administración
    # ==========================
    path('administrador/', admin_dashboard, name='admin_dashboard'),
    path('administrador/estadisticas/', admin_stats, name='admin_stats'),
    path('administrador/historial/', admin_historial, name='admin_historial'),
    path('administrador/sesiones/', admin_sesiones, name='admin_sesiones'),

    # ==========================
    # Perfil
    # ==========================
    path('perfil/', perfil, name='perfil'),

    # ==========================
    # PANEL ADMINISTRADOR - VEHICULOS
    # ==========================
    path('vehiculos-admin/', vehiculos_admin, name='vehiculos_admin'),
    path('vehiculos-admin/marca/<int:id>/editar/', vehiculo_editar_marca, name='vehiculo_editar_marca'),
    path('vehiculos-admin/modelo/<int:id>/editar/', vehiculo_editar_modelo, name='vehiculo_editar_modelo'),

    # ==========================
    # CAFETERÍA - CLIENTE
    # ==========================
    path('cafeteria/', cafeteria_menu, name='cafeteria_menu'),
    path('cafeteria/orden/crear/', cafeteria_orden_create, name='cafeteria_orden_create'),
    path('cafeteria/orden/<int:orden_id>/', cafeteria_orden_detalle, name='cafeteria_orden_detalle'),
    path('cafeteria/ordenes/activas/', cafeteria_ordenes_activas, name='cafeteria_ordenes_activas'),
    path('cafeteria/orden/<int:orden_id>/estado/<str:nuevo_estado>/', cafeteria_cambiar_estado, name='cafeteria_cambiar_estado'),

    # ==========================
    # FACTURACIÓN
    # ==========================
    path('factura/crear/<int:cita_id>/', factura_crear, name='factura_crear'),
    path('factura/<int:factura_id>/', factura_detalle, name='factura_detalle'),
    path('factura/<int:factura_id>/pagar/', factura_pagar, name='factura_pagar'),
    path('facturas/', factura_list, name='factura_list'),

    # ==========================
    # ADMINISTRACIÓN DE CAFETERÍA
    # ==========================
    path('administrador/cafeteria/categorias/', admin_categorias, name='admin_categorias'),
    path('administrador/cafeteria/categoria/crear/', admin_categoria_create, name='admin_categoria_create'),
    path('administrador/cafeteria/categoria/<int:categoria_id>/editar/', admin_categoria_edit, name='admin_categoria_edit'),
    path('administrador/cafeteria/categoria/<int:categoria_id>/toggle/', admin_categoria_toggle, name='admin_categoria_toggle'),
    path('administrador/cafeteria/categoria/<int:categoria_id>/eliminar/', admin_categoria_delete, name='admin_categoria_delete'),
    path('administrador/cafeteria/productos/', admin_productos, name='admin_productos'),
    path('administrador/cafeteria/producto/crear/', admin_producto_create, name='admin_producto_create'),
    path('administrador/cafeteria/producto/<int:producto_id>/editar/', admin_producto_edit, name='admin_producto_edit'),
    path('administrador/cafeteria/producto/<int:producto_id>/toggle/', admin_producto_toggle, name='admin_producto_toggle'),
    path('administrador/cafeteria/producto/<int:producto_id>/eliminar/', admin_producto_delete, name='admin_producto_delete'),
    
    # ==========================
    # SESIONES DE EMPLEADOS
    # ==========================
    path('administrador/sesiones/', admin_sesiones, name='admin_sesiones'),
    path('administrador/sesiones/finalizar/<int:sesion_id>/', admin_sesion_finalizar, name='admin_sesion_finalizar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)