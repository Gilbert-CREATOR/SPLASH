"""
Tareas Automatizadas - B&B Car Wash
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .services.notifications import NotificationService, NotificationScheduler
from .models import Cita, Producto
import logging

logger = logging.getLogger(__name__)


@shared_task
def enviar_recordatorios_citas():
    """
    Tarea automatizada para enviar recordatorios de citas (24 horas antes)
    Se ejecuta todos los días a las 8:00 AM
    """
    try:
        scheduler = NotificationScheduler()
        resultados = scheduler.send_recordatorios_diarios()
        
        logger.info(f"Recordatorios enviados: {len(resultados)} citas procesadas")
        return {
            'status': 'success',
            'enviados': len(resultados),
            'detalles': resultados
        }
    except Exception as e:
        logger.error(f"Error enviando recordatorios: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def verificar_stock_bajo():
    """
    Tarea automatizada para verificar y alertar sobre stock bajo
    Se ejecuta cada 2 horas durante el día
    """
    try:
        scheduler = NotificationScheduler()
        resultados = scheduler.verificar_stock_bajo()
        
        logger.info(f"Alertas de stock enviadas: {len(resultados)} productos")
        return {
            'status': 'success',
            'alertas': len(resultados),
            'detalles': resultados
        }
    except Exception as e:
        logger.error(f"Error verificando stock: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def enviar_reporte_diario():
    """
    Tarea automatizada para enviar reporte diario de operaciones
    Se ejecuta todos los días a las 6:00 PM
    """
    try:
        scheduler = NotificationScheduler()
        resultado = scheduler.enviar_reporte_diario()
        
        logger.info(f"Reporte diario enviado: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error enviando reporte diario: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def enviar_notificacion_cita_confirmada(cita_id):
    """
    Tarea para enviar notificación de confirmación de cita
    Se ejecuta de forma asíncrona cuando se agenda una cita
    """
    try:
        from .models import Cita
        cita = Cita.objects.get(id=cita_id)
        
        notification_service = NotificationService()
        resultado = notification_service.send_cita_confirmation(cita)
        
        logger.info(f"Notificación de confirmación enviada para cita {cita_id}: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error enviando confirmación cita {cita_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def enviar_notificacion_cita_recordatorio(cita_id):
    """
    Tarea para enviar recordatorio de cita específica
    """
    try:
        from .models import Cita
        cita = Cita.objects.get(id=cita_id)
        
        notification_service = NotificationService()
        resultado = notification_service.send_cita_recordatorio(cita)
        
        logger.info(f"Recordatorio enviado para cita {cita_id}: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error enviando recordatorio cita {cita_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def enviar_notificacion_orden_lista(orden_id):
    """
    Tarea para enviar notificación cuando orden de cafetería está lista
    """
    try:
        from .models import OrdenCafeteria
        orden = OrdenCafeteria.objects.get(id=orden_id)
        
        notification_service = NotificationService()
        resultado = notification_service.send_orden_lista(orden)
        
        logger.info(f"Notificación de orden lista enviada para orden {orden_id}: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error enviando notificación orden lista {orden_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def enviar_notificacion_factura_generada(factura_id):
    """
    Tarea para enviar notificación cuando se genera una factura
    """
    try:
        from .models import Factura
        factura = Factura.objects.get(id=factura_id)
        
        notification_service = NotificationService()
        resultado = notification_service.send_factura_generada(factura)
        
        logger.info(f"Notificación de factura enviada para factura {factura_id}: {resultado}")
        return resultado
    except Exception as e:
        logger.error(f"Error enviando notificación factura {factura_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def limpiar_notificaciones_antiguas():
    """
    Tarea para limpiar registros de notificaciones antiguas
    Se ejecuta una vez por semana
    """
    try:
        from .models import NotificacionLog  # Asumiendo que tienes este modelo
        
        # Eliminar notificaciones de más de 30 días
        fecha_limite = timezone.now() - timedelta(days=30)
        
        eliminados = NotificacionLog.objects.filter(
            fecha_envio__lt=fecha_limite
        ).delete()[0]
        
        logger.info(f"Limpiadas {eliminados} notificaciones antiguas")
        return {
            'status': 'success',
            'eliminados': eliminados
        }
    except Exception as e:
        logger.error(f"Error limpiando notificaciones antiguas: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def verificar_citas_vencidas():
    """
    Tarea para verificar y actualizar citas vencidas automáticamente
    Se ejecuta cada hora
    """
    try:
        from .models import Cita
        
        ahora = timezone.now()
        hoy = ahora.date()
        
        # Cancelar citas que pasaron su hora y no fueron atendidas
        citas_vencidas = Cita.objects.filter(
            fecha__lt=hoy,
            estado__in=['pendiente', 'confirmada']
        )
        
        # También citas de hoy que ya pasaron su hora
        hora_actual = ahora.time()
        citas_hoy_vencidas = Cita.objects.filter(
            fecha=hoy,
            hora__lt=hora_actual,
            estado__in=['pendiente', 'confirmada']
        )
        
        total_vencidas = citas_vencidas.count() + citas_hoy_vencidas.count()
        
        # Actualizar estado a 'cancelada' automáticamente
        citas_vencidas.update(estado='cancelada')
        citas_hoy_vencidas.update(estado='cancelada')
        
        logger.info(f"Se cancelaron {total_vencidas} citas vencidas automáticamente")
        return {
            'status': 'success',
            'canceladas': total_vencidas
        }
    except Exception as e:
        logger.error(f"Error verificando citas vencidas: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def actualizar_estadisticas_diarias():
    """
    Tarea para actualizar estadísticas diarias
    Se ejecuta cada noche a medianoche
    """
    try:
        from .models import EstadisticasDiarias  # Asumiendo que tienes este modelo
        
        hoy = timezone.now().date()
        
        # Calcular estadísticas del día
        from django.db.models import Count, Sum, Avg
        from .models import Cita, Factura
        
        citas_hoy = Cita.objects.filter(fecha=hoy)
        facturas_hoy = Factura.objects.filter(fecha_emision=hoy)
        
        stats = {
            'fecha': hoy,
            'citas_total': citas_hoy.count(),
            'citas_confirmadas': citas_hoy.filter(estado='confirmada').count(),
            'citas_finalizadas': citas_hoy.filter(estado='finalizada').count(),
            'ingresos_totales': facturas_hoy.aggregate(total=Sum('total_factura'))['total'] or 0,
            'ticket_promedio': facturas_hoy.aggregate(promedio=Avg('total_factura'))['promedio'] or 0,
        }
        
        # Guardar o actualizar estadísticas
        estadistica, created = EstadisticasDiarias.objects.update_or_create(
            fecha=hoy,
            defaults=stats
        )
        
        logger.info(f"Estadísticas diarias actualizadas para {hoy}: {stats}")
        return {
            'status': 'success',
            'fecha': hoy,
            'stats': stats
        }
    except Exception as e:
        logger.error(f"Error actualizando estadísticas diarias: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
