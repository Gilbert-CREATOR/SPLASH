from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from .models import Cita, Servicio, Vehiculo, Marca, Modelo, Factura, OrdenCafeteria, Producto, DetalleOrden, Categoria
from .forms import CitaForm, PerfilForm, ProductoForm, CategoriaForm, MarcaForm, ModeloForm, OrdenCafeteriaForm, FacturaForm
from .services.notifications import NotificationService
import uuid
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import threading
import logging
from django.contrib.admin.views.decorators import staff_member_required
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.db.models.functions import ExtractMonth, TruncDate
from django.utils.timezone import now
from django.utils.crypto import get_random_string
import json

# Importación condicional de tareas de Celery
try:
    from .tasks import enviar_notificacion_cita_confirmada
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery no disponible. Las notificaciones serán síncronas.")
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import time as time_type


logger = logging.getLogger(__name__)


# ===================================
#       VISTAS DEL CLIENTE
# ===================================

def inicio(request):
    """Página de inicio con listado de servicios."""
    servicios = Servicio.objects.all()
    return render(request, 'pages/cliente/inicio.html', {'servicios': servicios})


def zonadeservicio(request):
    """Página de zona de servicios (informativa)."""
    return render(request, 'pages/cliente/servicios.html')


def sobrenosotros(request):
    """Página sobre nosotros (informativa)."""
    return render(request, 'pages/cliente/servicios.html')


def agendar_cita(request):
    servicios = Servicio.objects.all()
    fecha = None

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        form = CitaForm(request.POST, fecha=fecha)

        marca_id = request.POST.get('marca')
        modelo_id = request.POST.get('modelo')
        servicio_id = request.POST.get('servicio')

        # Validaciones
        if not marca_id:
            form.add_error(None, "Debes seleccionar una marca válida.")
        if not modelo_id:
            form.add_error(None, "Debes seleccionar un modelo válido.")
        if not servicio_id:
            form.add_error(None, "Debes seleccionar un servicio.")

        if form.is_valid():
            cita = form.save(commit=False)
            cita.marca = Marca.objects.get(id=marca_id)
            cita.modelo = Modelo.objects.get(id=modelo_id)
            cita.servicio = Servicio.objects.get(id=servicio_id)
            if request.user.is_authenticated:
                cita.agendado_por = request.user
            cita.save()
            
            # Enviar notificaciones automáticas de forma asíncrona
            try:
                if CELERY_AVAILABLE:
                    enviar_notificacion_cita_confirmada.delay(cita.id)
                    messages.success(request, "Tu cita ha sido agendada correctamente. Te enviaremos un email de confirmación.")
                else:
                    # Fallback a envío síncrono si Celery no está disponible
                    notification_service = NotificationService()
                    resultado = notification_service.send_cita_confirmation(cita)
                    
                    if resultado['email_sent']:
                        messages.success(request, "Tu cita ha sido agendada correctamente. Te hemos enviado un email de confirmación.")
                    else:
                        messages.success(request, "Tu cita ha sido agendada correctamente.")
            except Exception as e:
                # Si falla el envío, no impedir el agendamiento
                try:
                    notification_service = NotificationService()
                    resultado = notification_service.send_cita_confirmation(cita)
                    
                    if resultado['email_sent']:
                        messages.success(request, "Tu cita ha sido agendada correctamente. Te hemos enviado un email de confirmación.")
                    else:
                        messages.success(request, "Tu cita ha sido agendada correctamente.")
                except Exception as sync_error:
                    messages.success(request, "Tu cita ha sido agendada correctamente.")
                    logger.error(f"Error enviando notificaciones para cita {cita.id}: {str(e)} / {str(sync_error)}")
            
            return redirect('inicio')
        else:
            print(form.errors) 

    else:
        form = CitaForm(fecha=fecha)

    return render(request, 'pages/cliente/agendar.html', {
        'form': form,
        'servicios': servicios
    })

# ===================================
#       FUNCIONES DE CORREO
# ===================================

def enviar_correo_cita(cita):
    """
    Envia correo al cliente según el estado de la cita.
    Retorna True si se envió correctamente.
    """
    if not cita.email:
        return False

    destinatario = (cita.email or "").strip()
    if not destinatario:
        return False

    fecha_formateada = cita.fecha.strftime('%d/%m/%Y') if hasattr(cita.fecha, 'strftime') else str(cita.fecha)
    if isinstance(cita.hora, time_type):
        hora_formateada = cita.hora.strftime("%H:%M")
    else:
        hora_formateada = str(cita.hora)

    if cita.estado == "confirmada":
        asunto = "Cita confirmada - CarWash"
        mensaje = f"Hola {cita.nombre}, tu cita con el servicio {cita.servicio} ha sido CONFIRMADA el {fecha_formateada} a las {hora_formateada}."
        html_mensaje = f"""<div style="font-family: Arial; color: #333;">
            <h2 style="color: #2E86C1;">¡Hola {cita.nombre}!</h2>
            <p>Tu cita ha sido <b style="color:green;">CONFIRMADA</b> ✅</p>
            <p><b>Servicio:</b> {cita.servicio}<br><b>Fecha:</b> {fecha_formateada}<br><b>Hora:</b> {hora_formateada}<br><b>Vehículo:</b> {cita.modelo}</p>
        </div>"""

    elif cita.estado == "en_proceso":
        asunto = "Tu vehículo está en proceso - CarWash"
        mensaje = f"Hola {cita.nombre}, tu vehículo está EN PROCESO."
        html_mensaje = f"""<div><p>Tu vehículo {cita.modelo} está EN PROCESO 🔧</p></div>"""

    elif cita.estado == "finalizada":
        asunto = "Servicio finalizado - CarWash"
        mensaje = f"Hola {cita.nombre}, tu servicio ha sido FINALIZADO."
        html_mensaje = f"""<div><p>Tu servicio {cita.modelo} ha sido FINALIZADO ✅</p></div>"""

    elif cita.estado == "cancelada":
        asunto = "Cita cancelada - CarWash"
        mensaje = f"Hola {cita.nombre}, tu cita ha sido CANCELADA."
        html_mensaje = f"""<div><p>Tu cita para el vehiculo {cita.modelo} ha sido CANCELADA ❌</p></div>"""
    else:
        return False

    try:
        # EmailMultiAlternatives es más confiable que html_message en algunos backends
        email = EmailMultiAlternatives(
            subject=asunto,
            body=strip_tags(html_mensaje) or mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        email.attach_alternative(html_mensaje, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.exception(f"Error enviando correo a {destinatario}")
        return False


@staff_member_required
def cambiar_estado_cita(request, id, nuevo_estado):
    """
    Cambia el estado de una cita y envía correo al cliente.
    Envío síncrono: si falla, mostramos el error real.
    """
    if request.method != "POST":
        return redirect('empleado_dashboard')

    cita = get_object_or_404(Cita, id=id)
    cita.estado = nuevo_estado
    cita.save()

    if not (cita.email or "").strip():
        messages.warning(request, "Estado actualizado, pero el cliente no tiene email registrado.")
        return redirect('empleado_dashboard')

    try:
        enviado = enviar_correo_cita(cita)
        cita.correo_enviado = bool(enviado)
        cita.save(update_fields=["correo_enviado"])
        if enviado:
            messages.success(request, "Estado actualizado y correo enviado correctamente.")
        else:
            messages.error(request, "Estado actualizado, pero no se pudo enviar el correo. Revisa la configuración de correo.")
    except Exception as e:
        cita.correo_enviado = False
        cita.save(update_fields=["correo_enviado"])
        messages.error(request, f"Estado actualizado, pero falló el envío de correo: {e}")

    return redirect('empleado_dashboard')

# ===================================
# CORREOS DE APROXIMACION DE CITA "RECORDATORIO"
# ===================================

def enviar_recordatorios_citas():
    """
    Envía recordatorio 1 hora y 30 minutos antes de la cita.
    """

    ahora = timezone.now()

    citas = Cita.objects.filter(
        estado="confirmada",
        recordatorio_enviado=False
    )

    for cita in citas:

        try:
            # `hora` puede ser time() o string según origen/migraciones
            if isinstance(cita.hora, time_type):
                hora_obj = cita.hora
            else:
                hora_str = str(cita.hora)
                # Soporta "HH:MM" o "HH:MM:SS"
                fmt = "%H:%M:%S" if len(hora_str.split(":")) == 3 else "%H:%M"
                hora_obj = datetime.strptime(hora_str, fmt).time()

            fecha_hora_cita = datetime.combine(cita.fecha, hora_obj)
            fecha_hora_cita = timezone.make_aware(fecha_hora_cita)

            tiempo_restante = fecha_hora_cita - ahora

            # 1 hora y 30 minutos
            if timedelta(minutes=89) <= tiempo_restante <= timedelta(minutes=91):

                asunto = "Recordatorio de cita - CarWash"

                mensaje = (
                    f"Hola {cita.nombre},\n\n"
                    f"Te recordamos que tu cita para el servicio {cita.servicio} "
                    f"es hoy a las {cita.hora}.\n\n"
                    "Te esperamos en nuestro CarWash."
                )

                html_mensaje = f"""
                <div style="font-family: Arial;">
                    <h2>🚗 Recordatorio de cita</h2>
                    <p>Hola <b>{cita.nombre}</b>,</p>
                    <p>Tu cita está próxima.</p>
                    <p>
                    <b>Servicio:</b> {cita.servicio}<br>
                    <b>Fecha:</b> {cita.fecha}<br>
                    <b>Hora:</b> {cita.hora}
                    </p>
                    <p>Te esperamos en nuestro CarWash.</p>
                </div>
                """

                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [cita.email],
                    fail_silently=False,
                    html_message=html_mensaje
                )

                cita.recordatorio_enviado = True
                cita.save()

        except Exception as e:
            logger.error(f"Error enviando recordatorio: {e}")



# ===================================
#       VISTAS DEL EMPLEADO
# ===================================

def login(request):
    return render(request, 'pages/empleado/login_empleado.html')


@staff_member_required
def dashboard(request):
    """Dashboard principal para empleados - solo información básica."""
    # Estadísticas básicas de citas
    total_citas = Cita.objects.count()
    citas_hoy = Cita.objects.filter(fecha=timezone.now().date()).count()
    citas_pendientes = Cita.objects.filter(estado='pendiente').count()
    citas_confirmadas = Cita.objects.filter(estado='confirmada').count()
    
    # Citas recientes (últimas 10)
    citas_recientes = Cita.objects.all().order_by('-fecha', '-hora')[:10]
    
    context = {
        'citas': citas_recientes,
        'total_citas': total_citas,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
        'citas_confirmadas': citas_confirmadas,
    }
    return render(request, 'pages/empleado/index.html', context)


@staff_member_required
def empleado_dashboard(request):
    """Dashboard alternativo de empleado (mismo que dashboard)."""
    # Estadísticas básicas de citas
    total_citas = Cita.objects.count()
    citas_hoy = Cita.objects.filter(fecha=timezone.now().date()).count()
    citas_pendientes = Cita.objects.filter(estado='pendiente').count()
    citas_confirmadas = Cita.objects.filter(estado='confirmada').count()
    
    # Citas recientes (últimas 10)
    citas_recientes = Cita.objects.all().order_by('-fecha', '-hora')[:10]
    
    context = {
        'citas': citas_recientes,
        'total_citas': total_citas,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
        'citas_confirmadas': citas_confirmadas,
    }
    return render(request, 'pages/empleado/index.html', context)


@login_required
def perfil(request):
    user = request.user
    from .models import perfil

    perfil_obj, created = perfil.objects.get_or_create(
        user=user,
        defaults={
            'nombre': user.get_full_name() or user.username,
            'email': user.email
        }
    )

    form_password = PasswordChangeForm(user, request.POST or None)
    form_foto = PerfilForm(
        request.POST or None,
        request.FILES or None,
        instance=perfil_obj
    )

    if request.method == 'POST':
        if 'cambiar_contrasena' in request.POST:
            if form_password.is_valid():
                user = form_password.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('perfil')
            messages.error(request, 'Corrige los errores del formulario.')

        elif 'borrar_usuario' in request.POST:
            user.delete()
            logout(request)
            return redirect('inicio')

        elif 'foto_perfil' in request.FILES:
            if form_foto.is_valid():
                form_foto.save()
                messages.success(request, 'Foto de perfil actualizada.')
                return redirect('perfil')
            messages.error(request, 'Error al subir la foto.')

    return render(request, 'pages/empleado/perfil.html', {
        'user': user,
        'perfil': perfil_obj,
        'form': form_password,
        'form_foto': form_foto
    })


@login_required
def cambiar_contrasena(request):
    """Cambiar contraseña del empleado."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pages/empleado/cambiar_contrasena.html', {'form': form})


@login_required
def borrar_usuario(request):
    """Eliminar usuario actual."""
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('inicio')
    return render(request, 'pages/empleado/borrar_usuario.html')


@login_required
def eliminar_cita(request, id):
    """Eliminar una cita por ID."""
    cita = get_object_or_404(Cita, id=id)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada correctamente")
    return redirect('empleado_dashboard')


@login_required
def dashboard_citas(request):
    """Vista de todas las citas para dashboard."""
    citas = Cita.objects.order_by('fecha', 'hora')
    return render(request, 'dashboard/citas.html', {'citas': citas})


@login_required
def dashboard_cita_detalle(request, id):
    """Detalle de una cita específica."""
    cita = Cita.objects.get(id=id)
    return render(request, 'dashboard/detalle.html', {'cita': cita})


@login_required
def empleado_vehiculos(request):
    """Lista de vehículos en el dashboard."""
    vehiculos = Vehiculo.objects.select_related('marca', 'modelo').order_by('marca__nombre', 'modelo__nombre')
    return render(request, 'dashboard/vehiculos.html', {'vehiculos': vehiculos})


# ===================================
#       AUTENTICACIÓN
# ===================================

def login_view(request):
    """Login de empleados."""
    if request.user.is_authenticated:
        return redirect('empleado_dashboard')

    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Por favor, complete todos los campos.")
            return render(request, 'pages/empleado/login_empleado.html')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Credenciales inválidas. Inténtelo de nuevo.")
            return render(request, 'pages/empleado/login_empleado.html')

        auth_login(request, user)
        messages.success(request, f"Bienvenido {user.first_name or user.username}!")
        return redirect('empleado_dashboard')

    return render(request, 'pages/empleado/login_empleado.html')


def registro(request):
    """Registro de un nuevo empleado."""
    if request.user.is_authenticated:
        return redirect('empleado_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not password1 or not password2:
            messages.error(request, 'Complete todos los campos obligatorios.')
            return render(request, 'pages/empleado/registro_empleado.html')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'pages/empleado/registro_empleado.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuario ya existe.')
            return render(request, 'pages/empleado/registro_empleado.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        auth_login(request, user)
        messages.success(request, f'Bienvenido {user.username}')
        return redirect('empleado_dashboard')

    return render(request, 'pages/empleado/registro_empleado.html')


def logout_view(request):
    """Cerrar sesión del empleado."""
    logout(request)
    return redirect('inicio')


# ===================================
#       AUTOCOMPLETE MARCAS / MODELOS
# ===================================

def buscar_marcas(request):
    """Buscar marcas para autocomplete."""
    q = request.GET.get('q', '')
    marcas = Marca.objects.filter(nombre__icontains=q).order_by('nombre')[:10]
    data = [{'id': marca.id, 'nombre': marca.nombre} for marca in marcas]
    return JsonResponse(data, safe=False)


def buscar_modelos(request):
    """Buscar modelos según la marca para autocomplete."""
    q = request.GET.get('q', '')
    marca_id = request.GET.get('marca_id')
    if not marca_id:
        return JsonResponse([], safe=False)
    modelos = Modelo.objects.filter(marca_id=marca_id, nombre__icontains=q).order_by('nombre')[:10]
    data = [{'id': modelo.id, 'nombre': modelo.nombre} for modelo in modelos]
    return JsonResponse(data, safe=False)


def api_marcas(request):
    """API de marcas (similar a buscar_marcas)."""
    q = request.GET.get('q', '')
    marcas = Marca.objects.filter(nombre__icontains=q).order_by('nombre')[:10]
    data = [{"id": marca.id, "nombre": marca.nombre} for marca in marcas]
    return JsonResponse(data, safe=False)


def api_modelos(request):
    """API de modelos según la marca (similar a buscar_modelos)."""
    q = request.GET.get('q', '')
    marca_id = request.GET.get('marca_id')
    if not marca_id:
        return JsonResponse([], safe=False)
    modelos = Modelo.objects.filter(marca_id=marca_id, nombre__icontains=q).order_by('nombre')[:10]
    data = [{"id": modelo.id, "nombre": modelo.nombre} for modelo in modelos]
    return JsonResponse(data, safe=False)


# ===================================
#       VISTAS DE SERVICIOS
# ===================================
@login_required
def servicio_list(request):
    servicios = Servicio.objects.all().order_by('id')
    q = request.GET.get('q', '').strip()
    if q:
        servicios = servicios.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )
    return render(request, 'panel/servicios/list.html', {'servicios': servicios, 'q': q})

@login_required
def servicio_create(request):
    form = ServicioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/servicios/form.html', {'form': form, 'titulo': 'Nuevo Servicio'})

@login_required
def servicio_edit(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    form = ServicioForm(request.POST or None, instance=servicio)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/servicios/form.html', {'form': form, 'titulo': 'Editar Servicio'})

@login_required
def servicio_toggle(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    servicio.activo = not servicio.activo
    servicio.save()
    return redirect('servicio_list')


@login_required
def servicio_delete(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, "Servicio eliminado.")
        return redirect('servicio_list')
    return redirect('servicio_list')

# ===================================
#       VISTAS DE USUARIOS
# ===================================

def admin_usuario_create(request):
    form = ServicioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/usuarios/form.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@login_required
def admin_usuario_edit(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    form = ServicioForm(request.POST or None, instance=servicio)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/usuarios/form.html', {'form': form, 'titulo': 'Editar Usuario'})

@login_required
def admin_usuario_delete(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    servicio.delete()
    return redirect('servicio_list')

# ===================================
#       DECORADOR DE ADMIN
# ===================================
def admin_required(view_func):
    """Decorator para restringir vista solo a administradores."""
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)

# ===================================
#       DASHBOARD ADMINISTRADOR
# ===================================
@admin_required
def admin_dashboard(request):
    empleados = User.objects.filter(is_staff=True)
    return render(request, 'pages/administrador/dashboard.html', {
        'empleados': empleados
    })
# ===================================
#       VEHICULOS ADMINISTRADOR
# ===================================
@admin_required
def vehiculos_admin(request):

    marca_form = MarcaForm()
    modelo_form = ModeloForm()

    if request.method == "POST":

        # AGREGAR MARCA
        if "agregar_marca" in request.POST:
            marca_form = MarcaForm(request.POST)

            if marca_form.is_valid():
                marca_form.save()
                messages.success(request, "Marca agregada correctamente")
                return redirect("vehiculos_admin")

        # AGREGAR MODELO
        if "agregar_modelo" in request.POST:
            modelo_form = ModeloForm(request.POST)

            if modelo_form.is_valid():
                modelo_form.save()
                messages.success(request, "Modelo agregado correctamente")
                return redirect("vehiculos_admin")

        # ELIMINAR MARCA
        if "eliminar_marca" in request.POST:
            marca_id = request.POST.get("marca_id")
            Marca.objects.filter(id=marca_id).delete()
            messages.success(request, "Marca eliminada")
            return redirect("vehiculos_admin")

        # ELIMINAR MODELO
        if "eliminar_modelo" in request.POST:
            modelo_id = request.POST.get("modelo_id")
            Modelo.objects.filter(id=modelo_id).delete()
            messages.success(request, "Modelo eliminado")
            return redirect("vehiculos_admin")

    # BUSCADOR
    search = request.GET.get("search")

    if search:
        marcas = Marca.objects.filter(nombre__icontains=search)
    else:
        marcas = Marca.objects.all()

    context = {
        "marca_form": marca_form,
        "modelo_form": modelo_form,
        "marcas": marcas
    }

    return render(request, "pages/administrador/vehiculo.html", context)


@admin_required
def vehiculo_editar_marca(request, id):
    marca = get_object_or_404(Marca, id=id)
    form = MarcaForm(request.POST or None, instance=marca)
    if form.is_valid():
        form.save()
        messages.success(request, "Marca actualizada.")
        return redirect("vehiculos_admin")
    return render(request, "pages/administrador/vehiculo_editar_marca.html", {"form": form, "marca": marca})


@admin_required
def vehiculo_editar_modelo(request, id):
    modelo = get_object_or_404(Modelo, id=id)
    form = ModeloForm(request.POST or None, instance=modelo)
    if form.is_valid():
        form.save()
        messages.success(request, "Modelo actualizado.")
        return redirect("vehiculos_admin")
    return render(request, "pages/administrador/vehiculo_editar_modelo.html", {"form": form, "modelo": modelo})

# ===================================
#       CREAR EMPLEADO
# ===================================
@admin_required
def admin_empleado_create(request):
    """Crear empleado - Solo para superusuario"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear empleados.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True

            # 🔐 CONTRASEÑA TEMPORAL EN TEXTO PLANO
            password = get_random_string(10)

            # ⛔ IMPORTANTE: set_password, NO user.password =
            user.set_password(password)
            user.save()

            # 🎭 CREAR PERFIL CON ROL
            rol_seleccionado = form.cleaned_data.get('rol', 'empleado')
            perfil_obj, created = perfil.objects.get_or_create(
                user=user,
                defaults={
                    'nombre': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'rol': rol_seleccionado
                }
            )
            
            if not created:
                # Si el perfil ya existía, actualizar el rol
                perfil_obj.rol = rol_seleccionado
                perfil_obj.save()

            # 📧 CORREO
            if user.email:
                send_mail(
                    subject='Acceso al sistema',
                    message=(
                        f'Hola {user.username},\n\n'
                        'Has sido agregado como empleado.\n\n'
                        f'Usuario: {user.username}\n'
                        f'Contraseña: {password}\n'
                        f'Rol: {rol_seleccionado.title()}\n\n'
                        'Por favor cambia tu contraseña al iniciar sesión.\n\n'
                        'Saludos.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            messages.success(
                request,
                f'Empleado {user.username} creado con rol "{rol_seleccionado.title()}" y correo enviado.'
            )
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = EmpleadoForm()

    return render(
        request,
        'pages/administrador/empleado_form.html',
        {'form': form, 'titulo': 'Nuevo Empleado'}
    )

# ===================================
#       ELIMINAR EMPLEADO
# ===================================
@admin_required
def admin_empleado_delete(request, id):
    empleado = get_object_or_404(User, id=id, is_staff=True)
    empleado.delete()
    messages.success(request, f'Empleado {empleado.username} eliminado correctamente.')
    return redirect('admin_dashboard')

# ===================================
#       ESTADÍSTICAS ADMINISTRADOR
# ===================================

@admin_required
def admin_stats(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import ExtractMonth, TruncDate
    from django.utils.timezone import now
    from datetime import timedelta
    import json

    # ===============================
    # Citas por Estado
    # ===============================
    citas_estado_qs = (
        Cita.objects.values('estado')
        .annotate(total=Count('id'))
        .order_by('estado')
    )

    estados = [c['estado'] for c in citas_estado_qs]
    totales_estado = [c['total'] for c in citas_estado_qs]


    # ===============================
    # Ingresos por Mes (solo finalizadas)
    # ===============================
    ingresos_mes_qs = (
        Cita.objects.filter(estado='finalizada')
        .annotate(mes=ExtractMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('servicio__precio'))
        .order_by('mes')
    )

    meses = [c['mes'] for c in ingresos_mes_qs]
    totales_ingresos = [float(c['total']) if c['total'] else 0 for c in ingresos_mes_qs]


    # ===============================
    # Servicios más Populares
    # ===============================
    servicios_qs = (
        Cita.objects.values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    nombres_servicios = [c['servicio__nombre'] for c in servicios_qs]
    totales_servicios = [c['total'] for c in servicios_qs]


    # ===============================
    # Citas por Día
    # ===============================
    citas_dia_qs = (
        Cita.objects
        .annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    dias = [c['dia'].strftime('%d-%m-%Y') for c in citas_dia_qs]
    totales_dia = [c['total'] for c in citas_dia_qs]

    # ===============================
    # ESTADÍSTICAS DE CAFETERÍA
    # ===============================
    from .models import DetalleOrden, OrdenCafeteria, Producto
    
    # Productos más vendidos
    productos_mas_vendidos = DetalleOrden.objects.values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    # Productos populares (marcados como populares)
    productos_populares = Producto.objects.filter(popular=True, activo=True)[:5]
    
    # Órdenes de cafetería
    total_ordenes = OrdenCafeteria.objects.count()
    ordenes_hoy = OrdenCafeteria.objects.filter(fecha_hora__date=timezone.now().date()).count()
    
    # Ingresos totales de cafetería
    ingresos_cafeteria = OrdenCafeteria.objects.aggregate(
        total=Sum('total')
    )['total'] or 0


    # ===============================
    # Citas por Servicio (todos, con cantidad)
    # ===============================
    citas_por_servicio_qs = (
        Cita.objects.values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    citas_por_servicio_nombres = [c['servicio__nombre'] or 'Sin servicio' for c in citas_por_servicio_qs]
    citas_por_servicio_totales = [c['total'] for c in citas_por_servicio_qs]

    # ===============================
    # Ganancias totales (solo finalizadas)
    # ===============================
    ganancias_totales = Cita.objects.filter(estado='finalizada').aggregate(
        total=Sum('servicio__precio')
    )['total'] or 0

    # ===============================
    # Ingresos diarios (últimos 7 días)
    # ===============================
    hoy = now().date()
    ingresos_diarios = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        total_dia = Cita.objects.filter(estado='finalizada', fecha=d).aggregate(
            t=Sum('servicio__precio')
        )['t'] or 0
        ingresos_diarios.append({'fecha': d.strftime('%d/%m'), 'total': float(total_dia)})

    # ===============================
    # Ingresos semanales (últimas 4 semanas)
    # ===============================
    ingresos_semanales = []
    for i in range(3, -1, -1):
        fin_semana = hoy - timedelta(days=i*7)
        inicio_semana = fin_semana - timedelta(days=6)
        total_sem = Cita.objects.filter(
            estado='finalizada',
            fecha__gte=inicio_semana,
            fecha__lte=fin_semana
        ).aggregate(t=Sum('servicio__precio'))['t'] or 0
        ingresos_semanales.append({
            'label': f'{inicio_semana.strftime("%d/%m")}-{fin_semana.strftime("%d/%m")}',
            'total': float(total_sem)
        })

    context = {
        'estados': json.dumps(estados),
        'totales_estado': json.dumps(totales_estado),
        'meses': json.dumps(meses),
        'totales_ingresos': json.dumps(totales_ingresos),
        'nombres_servicios': json.dumps(nombres_servicios),
        'totales_servicios': json.dumps(totales_servicios),
        'dias': json.dumps(dias),
        'totales_dia': json.dumps(totales_dia),
        'citas_por_servicio_nombres': json.dumps(citas_por_servicio_nombres),
        'citas_por_servicio_totales': json.dumps(citas_por_servicio_totales),
        'ganancias_totales': float(ganancias_totales),
        'ingresos_diarios': ingresos_diarios,
        'ingresos_semanales': ingresos_semanales,
        
        # Estadísticas de cafetería
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_populares': productos_populares,
        'total_ordenes': total_ordenes,
        'ordenes_hoy': ordenes_hoy,
        'ingresos_cafeteria': ingresos_cafeteria,
    }

    return render(request, 'pages/administrador/stats_unified.html', context)

# ===================================
#       HISTORIAL DE CITAS (ADMIN)
# ===================================


def admin_historial(request):
    """
    Vista para mostrar todo el historial del negocio: citas, productos, facturas, etc.
    """
    # ==================== CITAS ====================
    citas = Cita.objects.select_related('servicio', 'marca', 'modelo', 'agendado_por').all().order_by('-fecha')

    # Filtros para citas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    servicio_id = request.GET.get('servicio')
    marca_id = request.GET.get('marca')
    modelo_id = request.GET.get('modelo')

    if fecha_inicio:
        citas = citas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        citas = citas.filter(fecha__lte=fecha_fin)
    if estado:
        citas = citas.filter(estado=estado)
    if servicio_id:
        citas = citas.filter(servicio_id=servicio_id)
    if marca_id:
        citas = citas.filter(marca_id=marca_id)
    if modelo_id:
        citas = citas.filter(modelo_id=modelo_id)

    # ==================== PRODUCTOS/CAFETERÍA ====================
    from .models import DetalleOrden, OrdenCafeteria, Factura
    
    # Órdenes de cafetería
    ordenes = OrdenCafeteria.objects.select_related('cita').all().order_by('-fecha_hora')
    
    # Detalles de productos vendidos
    productos_vendidos = DetalleOrden.objects.select_related('producto', 'orden').all().order_by('-orden__fecha_hora')
    
    # Facturas
    facturas = Factura.objects.select_related('cita').all().order_by('-fecha_emision')
    
    # Estadísticas generales
    from django.db.models import Sum, Count
    
    # Estadísticas de citas
    total_citas = citas.count()
    citas_completadas = citas.filter(estado='completada').count()
    
    # Estadísticas de cafetería
    total_ordenes = ordenes.count()
    ingresos_totales = ordenes.aggregate(total=Sum('total'))['total'] or 0
    
    # Productos más vendidos
    productos_top = productos_vendidos.values('producto__nombre').annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('subtotal')
    ).order_by('-total_vendido')[:10]
    
    # Estadísticas de facturas
    total_facturas = facturas.count()
    facturas_pagadas = facturas.filter(estado='pagada').count()
    ingresos_facturas = facturas.aggregate(total=Sum('total_factura'))['total'] or 0

    # ==================== PAGINACIÓN ====================
    paginator = Paginator(citas, 20)  # 20 citas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    q = request.GET.copy()
    q.pop('page', None)
    query_string = q.urlencode()

    context = {
        # Citas
        'page_obj': page_obj,
        'servicios': Servicio.objects.all(),
        'marcas': Marca.objects.all().order_by('nombre'),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': estado,
        'servicio_id': servicio_id,
        'marca_id': marca_id,
        'modelo_id': modelo_id,
        'query_string': query_string,
        
        # Cafetería y productos
        'ordenes': ordenes[:50],  # Últimas 50 órdenes
        'productos_vendidos': productos_vendidos[:100],  # Últimos 100 productos vendidos
        'facturas': facturas[:50],  # Últimas 50 facturas
        
        # Estadísticas generales
        'total_citas': total_citas,
        'citas_completadas': citas_completadas,
        'total_ordenes': total_ordenes,
        'ingresos_totales': ingresos_totales,
        'productos_top': productos_top,
        'total_facturas': total_facturas,
        'facturas_pagadas': facturas_pagadas,
        'ingresos_facturas': ingresos_facturas,
    }
    if marca_id:
        context['modelos'] = Modelo.objects.filter(marca_id=marca_id).order_by('nombre')
    else:
        context['modelos'] = []

    return render(request, 'pages/administrador/historial.html', context)


@admin_required
def admin_historial_descargar(request):
    """Descarga el historial de citas en CSV con los mismos filtros."""
    citas = Cita.objects.select_related('servicio', 'marca', 'modelo', 'agendado_por').all().order_by('-fecha', '-creada')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    servicio_id = request.GET.get('servicio')
    marca_id = request.GET.get('marca')
    modelo_id = request.GET.get('modelo')
    if fecha_inicio:
        citas = citas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        citas = citas.filter(fecha__lte=fecha_fin)
    if estado:
        citas = citas.filter(estado=estado)
    if servicio_id:
        citas = citas.filter(servicio_id=servicio_id)
    if marca_id:
        citas = citas.filter(marca_id=marca_id)
    if modelo_id:
        citas = citas.filter(modelo_id=modelo_id)

    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_citas.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Hora', 'Cliente', 'Teléfono', 'Email', 'Marca', 'Modelo', 'Servicio', 'Estado', 'Agendado por'])
    for c in citas:
        writer.writerow([
            c.fecha,
            c.hora,
            c.nombre,
            c.telefono or '',
            c.email or '',
            c.marca.nombre if c.marca else '',
            c.modelo.nombre if c.modelo else '',
            c.servicio.nombre if c.servicio else '',
            c.estado,
            c.agendado_por.get_full_name() or c.agendado_por.username if c.agendado_por else 'Cliente web',
        ])
    return response


# ===================================
#       VISTAS DE CAFETERÍA
# ===================================

def cafeteria_menu(request):
    """Menú de la cafetería para clientes"""
    categorias = Categoria.objects.filter(activo=True).order_by('orden', 'nombre')
    productos = Producto.objects.filter(activo=True, stock__gt=0).order_by('categoria__orden', 'categoria__nombre', 'nombre')
    
    # Obtener cita activa del cliente (si existe y está autenticado)
    cita_activa = None
    if request.user.is_authenticated:
        cita_activa = Cita.objects.filter(
            nombre__icontains=request.user.get_full_name() or request.user.username,
            estado__in=['pendiente', 'confirmada', 'en_proceso']
        ).first()
    
    context = {
        'categorias': categorias,
        'productos': productos,
        'cita_activa': cita_activa,
    }
    return render(request, 'pages/cafeteria/menu.html', context)


@login_required
def cafeteria_orden_create(request, cita_id=None):
    """Crear una nueva orden de cafetería"""
    cita = None
    if cita_id:
        cita = get_object_or_404(Cita, id=cita_id)
        
        # Verificar que la cita esté en proceso
        if cita.estado != 'en_proceso':
            messages.error(request, 'Solo se pueden agregar productos de cafetería a citas que están en proceso.')
            return redirect('dashboard_cita_detalle', cita.id)
    
    if request.method == 'POST':
        orden_form = OrdenCafeteriaForm(request.POST)
        if orden_form.is_valid():
            orden = orden_form.save(commit=False)
            orden.cita = cita
            orden.save()
            
            # Procesar productos del formulario
            productos_data = request.POST.getlist('productos')
            cantidades_data = request.POST.getlist('cantidades')
            notas_data = request.POST.getlist('notas')
            
            for i, producto_id in enumerate(productos_data):
                if producto_id and i < len(cantidades_data):
                    producto = get_object_or_404(Producto, id=producto_id)
                    cantidad = int(cantidades_data[i])
                    if cantidad > 0:
                        DetalleOrden.objects.create(
                            orden=orden,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=producto.precio,
                            notas=notas_data[i] if i < len(notas_data) else ''
                        )
                        
                        # Reducir stock
                        producto.stock -= cantidad
                        producto.save()
            
            # Calcular totales
            orden.calcular_totales()
            
            # MANTENER LA CITA EN PROCESO MIENTRAS HAYA ÓRDENES DE CAFETERÍA ACTIVAS
            # La cita solo se podrá finalizar manualmente desde el dashboard
            messages.success(request, 'Orden creada exitosamente. El servicio permanecerá en proceso hasta que se finalice desde el dashboard.')
            return redirect('cafeteria_orden_detalle', orden.id)
    else:
        orden_form = OrdenCafeteriaForm(initial={
            'cliente_nombre': request.user.get_full_name() or request.user.username,
            'cliente_telefono': getattr(request.user.perfil, 'telefono', '') if hasattr(request.user, 'perfil') else ''
        })
    
    context = {
        'orden_form': orden_form,
        'cita': cita,
        'productos': Producto.objects.filter(activo=True, stock__gt=0).order_by('categoria__orden', 'nombre')
    }
    return render(request, 'pages/cafeteria/orden_create.html', context)


@login_required
def cafeteria_orden_detalle(request, orden_id):
    """Ver detalles de una orden"""
    orden = get_object_or_404(OrdenCafeteria, id=orden_id)
    
    # Verificar si el usuario tiene permiso para ver esta orden
    if not request.user.is_staff and orden.cita and orden.cita.nombre != request.user.get_full_name():
        messages.error(request, 'No tienes permiso para ver esta orden')
        return redirect('cafeteria_menu')
    
    context = {
        'orden': orden,
        'detalles': orden.detalles.all()
    }
    return render(request, 'pages/cafeteria/orden_detalle.html', context)


@login_required
def cafeteria_ordenes_activas(request):
    """Ver órdenes activas (para empleados)"""
    if not request.user.is_staff:
        messages.error(request, 'Acceso denegado')
        return redirect('cafeteria_menu')
    
    ordenes = OrdenCafeteria.objects.filter(
        estado__in=['pendiente', 'en_preparacion', 'listo']
    ).order_by('-fecha_hora')
    
    context = {
        'ordenes': ordenes
    }
    return render(request, 'pages/cafeteria/ordenes_activas.html', context)


@login_required
def cafeteria_cambiar_estado(request, orden_id, nuevo_estado):
    """Cambiar estado de una orden"""
    if not request.user.is_staff:
        messages.error(request, 'Acceso denegado')
        return redirect('cafeteria_menu')
    
    orden = get_object_or_404(OrdenCafeteria, id=orden_id)
    
    if nuevo_estado in ['pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado']:
        orden.estado = nuevo_estado
        if nuevo_estado == 'entregado':
            orden.entregado_por = request.user
        orden.save()
        messages.success(request, f'Orden #{orden.id} actualizada a {nuevo_estado}')
    
    return redirect('cafeteria_ordenes_activas')


# ===================================
#       VISTAS DE FACTURACIÓN
# ===================================

@login_required
def factura_crear(request, cita_id):
    """Crear factura para una cita"""
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Verificar que la cita esté finalizada
    if cita.estado != 'finalizada':
        messages.error(request, 'Solo se pueden crear facturas para citas que han sido finalizadas.')
        return redirect('dashboard_cita_detalle', cita.id)
    
    # Verificar si ya existe una factura
    if hasattr(cita, 'factura'):
        messages.warning(request, 'Esta cita ya tiene una factura')
        return redirect('factura_detalle', cita.factura.id)
    
    # Buscar órdenes de cafetería no facturadas para esta cita
    orden_cafeteria = OrdenCafeteria.objects.filter(
        cita=cita,
        factura__isnull=True
    ).first()
    
    if request.method == 'POST':
        factura_form = FacturaForm(request.POST)
        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            factura.cita = cita
            factura.orden_cafeteria = orden_cafeteria
            factura.cliente_nombre = cita.nombre
            factura.cliente_telefono = cita.telefono
            factura.cliente_email = cita.email
            factura.emitida_por = request.user
            
            # Generar número de factura
            factura.generar_numero_factura()
            
            # Calcular totales
            factura.calcular_totales()
            
            # Actualizar estado
            factura.estado = 'emitida'
            factura.save()
            
            messages.success(request, f'Factura #{factura.numero_factura} creada exitosamente')
            return redirect('factura_detalle', factura.id)
    else:
        factura_form = FacturaForm()
    
    context = {
        'cita': cita,
        'orden_cafeteria': orden_cafeteria,
        'factura_form': factura_form
    }
    return render(request, 'pages/facturas/factura_crear.html', context)


@login_required
def factura_detalle(request, factura_id):
    """Ver detalles de una factura"""
    factura = get_object_or_404(Factura, id=factura_id)
    
    # Verificar permisos
    if not request.user.is_staff and factura.cliente_nombre != request.user.get_full_name():
        messages.error(request, 'No tienes permiso para ver esta factura')
        return redirect('inicio')
    
    context = {
        'factura': factura
    }
    return render(request, 'pages/facturas/factura_detalle.html', context)


@login_required
def factura_pagar(request, factura_id):
    """Marcar factura como pagada"""
    factura = get_object_or_404(Factura, id=factura_id)
    
    if not request.user.is_staff:
        messages.error(request, 'Acceso denegado')
        return redirect('factura_detalle', factura.id)
    
    if factura.estado != 'pagada':
        factura.estado = 'pagada'
        factura.fecha_pago = timezone.now()
        factura.save()
        messages.success(request, f'Factura #{factura.numero_factura} marcada como pagada')
    
    return redirect('factura_detalle', factura.id)


@login_required
def factura_list(request):
    """Lista de facturas con citas pendientes de facturar"""
    if request.user.is_staff:
        facturas = Factura.objects.all().order_by('-fecha_emision')
        
        # Citas pendientes de facturar
        citas_pendientes = Cita.objects.filter(
            estado__in=['en_proceso', 'finalizada']
        ).exclude(
            factura__isnull=False
        ).order_by('-fecha', '-hora')
        
        # Agrupar por estado para mejor visualización
        citas_en_proceso = citas_pendientes.filter(estado='en_proceso')
        citas_finalizadas = citas_pendientes.filter(estado='finalizada')
        
        # Calcular totales de cafetería para cada cita
        for cita in citas_pendientes:
            total_cafeteria = 0
            for orden in cita.ordenes_cafeteria.all():
                total_cafeteria += float(orden.total)
            cita.total_cafeteria = total_cafeteria
            # Calcular total estimado (servicio + cafetería) - ambos como float
            cita.total_estimado = float(cita.servicio.precio) + total_cafeteria
        
    else:
        # Clientes solo ven sus facturas
        facturas = Factura.objects.filter(
            cliente_nombre=request.user.get_full_name()
        ).order_by('-fecha_emision')
        
        # Citas pendientes del cliente
        citas_pendientes = Cita.objects.filter(
            nombre=request.user.get_full_name(),
            estado__in=['en_proceso', 'finalizada']
        ).exclude(
            factura__isnull=False
        ).order_by('-fecha', '-hora')
        
        citas_en_proceso = citas_pendientes.filter(estado='en_proceso')
        citas_finalizadas = citas_pendientes.filter(estado='finalizada')
        
        # Calcular totales de cafetería para cada cita
        for cita in citas_pendientes:
            total_cafeteria = 0
            for orden in cita.ordenes_cafeteria.all():
                total_cafeteria += float(orden.total)
            cita.total_cafeteria = total_cafeteria
            # Calcular total estimado (servicio + cafetería) - ambos como float
            cita.total_estimado = float(cita.servicio.precio) + total_cafeteria
    
    context = {
        'facturas': facturas,
        'citas_pendientes': citas_pendientes,
        'citas_en_proceso': citas_en_proceso,
        'citas_finalizadas': citas_finalizadas,
        'total_pendientes': citas_pendientes.count(),
    }
    return render(request, 'pages/facturas/factura_list.html', context)


# ===================================
#       ADMINISTRACIÓN DE CAFETERÍA
# ===================================

@staff_member_required
def admin_categorias(request):
    """Gestión de categorías - Para superusuario y admin"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para gestionar categorías.')
        return redirect('admin_productos')
    
    categorias = Categoria.objects.all().order_by('orden', 'nombre')
    return render(request, 'admin/cafeteria/categorias.html', {'categorias': categorias})


@staff_member_required
def admin_categoria_create(request):
    """Crear categoría - Para superusuario y admin"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para crear categorías.')
        return redirect('admin_productos')
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'admin/cafeteria/categoria_form.html', {'form': form, 'title': 'Crear Categoría'})


@staff_member_required
def admin_categoria_edit(request, categoria_id):
    """Editar categoría - Para superusuario y admin"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para editar categorías.')
        return redirect('admin_productos')
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'admin/cafeteria/categoria_form.html', {'form': form, 'title': 'Editar Categoría'})


@staff_member_required
def admin_categoria_toggle(request, categoria_id):
    """Activar/desactivar categoría - Para superusuario y admin"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para modificar categorías.')
        return redirect('admin_productos')
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.activo = not categoria.activo
    categoria.save()
    
    estado = "activada" if categoria.activo else "desactivada"
    messages.success(request, f'Categoría "{categoria.nombre}" {estado} exitosamente.')
    return redirect('admin_categorias')


@staff_member_required
def admin_categoria_delete(request, categoria_id):
    """Eliminar categoría - Para superusuario y admin"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para eliminar categorías.')
        return redirect('admin_productos')
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    # Verificar si hay productos asociados
    productos_count = categoria.productos.count()
    if productos_count > 0:
        messages.error(request, f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {productos_count} productos asociados. Elimina o mueve los productos primero.')
        return redirect('admin_categorias')
    
    if request.method == 'POST':
        nombre_categoria = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
        return redirect('admin_categorias')
    
    return render(request, 'admin/cafeteria/categoria_confirmar_eliminar.html', {'categoria': categoria})


@staff_member_required
def admin_productos(request):
    """Gestión de productos"""
    productos = Producto.objects.all().order_by('categoria__orden', 'categoria__nombre', 'nombre')
    return render(request, 'admin/cafeteria/productos.html', {'productos': productos})


@staff_member_required
def admin_producto_create(request):
    """Crear producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'admin/cafeteria/producto_form.html', {'form': form, 'title': 'Crear Producto'})


@staff_member_required
def admin_producto_edit(request, producto_id):
    """Editar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('admin_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'admin/cafeteria/producto_form.html', {'form': form, 'title': 'Editar Producto'})


@staff_member_required
def admin_producto_toggle(request, producto_id):
    """Activar/desactivar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    producto.activo = not producto.activo
    producto.save()
    
    estado = "activado" if producto.activo else "desactivado"
    messages.success(request, f'Producto "{producto.nombre}" {estado} exitosamente')
    return redirect('admin_productos')


@staff_member_required
def admin_producto_delete(request, producto_id):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si hay órdenes asociadas
    from .models import DetalleOrden
    ordenes_count = DetalleOrden.objects.filter(producto=producto).count()
    if ordenes_count > 0:
        messages.error(request, f'No se puede eliminar el producto "{producto.nombre}" porque está en {ordenes_count} órdenes. Considera desactivarlo en su lugar.')
        return redirect('admin_productos')
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        # Eliminar imagen si existe
        if producto.imagen:
            producto.imagen.delete(save=False)
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('admin_productos')
    
    return render(request, 'admin/cafeteria/producto_confirmar_eliminar.html', {'producto': producto})


# ===================================
#       SESIONES DE EMPLEADOS
# ===================================

@admin_required
def admin_sesiones(request):
    """Vista para administrar sesiones de empleados"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para ver sesiones de empleados.')
        return redirect('admin_dashboard')
    
    # Obtener todas las sesiones
    sesiones = SesionEmpleado.objects.select_related('empleado').all().order_by('-fecha_inicio')
    
    # Filtrar por empleado si se especifica
    empleado_id = request.GET.get('empleado')
    if empleado_id:
        sesiones = sesiones.filter(empleado_id=empleado_id)
    
    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado == 'activa':
        sesiones = sesiones.filter(activa=True)
    elif estado == 'finalizada':
        sesiones = sesiones.filter(activa=False)
    
    # Estadísticas
    total_sesiones = sesiones.count()
    sesiones_activas = sesiones.filter(activa=True).count()
    sesiones_finalizadas = sesiones.filter(activa=False).count()
    
    # Empleados para filtro
    empleados = User.objects.filter(is_staff=True).order_by('username')
    
    context = {
        'sesiones': sesiones,
        'total_sesiones': total_sesiones,
        'sesiones_activas': sesiones_activas,
        'sesiones_finalizadas': sesiones_finalizadas,
        'empleados': empleados,
        'empleado_id': empleado_id,
        'estado': estado,
    }
    
    return render(request, 'admin/sesiones/sesiones.html', context)


@admin_required
def admin_sesion_finalizar(request, sesion_id):
    """Finalizar una sesión de empleado"""
    if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin')):
        messages.error(request, 'No tienes permisos para finalizar sesiones.')
        return redirect('admin_dashboard')
    
    sesion = get_object_or_404(SesionEmpleado, id=sesion_id)
    
    if not sesion.activa:
        messages.warning(request, 'Esta sesión ya está finalizada.')
        return redirect('admin_sesiones')
    
    if request.method == 'POST':
        sesion.finalizar_sesion()
        messages.success(request, f'Sesión de {sesion.empleado.username} finalizada. Duración: {sesion.duracion_formateada}')
        return redirect('admin_sesiones')
    
    return render(request, 'admin/sesiones/confirmar_finalizar.html', {'sesion': sesion})


# ===================================
#       VIEWS DE ANALYTICS

