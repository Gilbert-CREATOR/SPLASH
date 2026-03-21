import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from ..models import Cita, OrdenCafeteria, Producto
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio de envío de emails"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@bbcarwash.com')
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Enviar email con soporte HTML"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Versión texto plano
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            else:
                text_part = MIMEText(strip_tags(html_content), 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Versión HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False


class NotificationService:
    """Servicio unificado de notificaciones (solo email)"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def send_cita_confirmation(self, cita):
        """Enviar confirmación de cita por email"""
        context = {
            'cita': cita,
            'servicio': cita.servicio,
            'fecha_formateada': cita.fecha.strftime('%d/%m/%Y'),
            'hora_formateada': cita.hora.strftime('%I:%M %p'),
            'nombre_cliente': cita.nombre,
        }
        
        # Email de confirmación
        html_content = render_to_string('emails/cita_confirmacion.html', context)
        text_content = render_to_string('emails/cita_confirmacion.txt', context)
        
        email_sent = self.email_service.send_email(
            to_email=cita.email,
            subject=f'✅ Confirmación de Cita - B&B Car Wash ({cita.fecha.strftime("%d/%m/%Y")})',
            html_content=html_content,
            text_content=text_content
        )
        
        return {
            'email_sent': email_sent,
            'sms_sent': False,  # SMS deshabilitado
            'cita_id': cita.id
        }
    
    def send_cita_recordatorio(self, cita):
        """Enviar recordatorio de cita (24 horas antes)"""
        context = {
            'cita': cita,
            'servicio': cita.servicio,
            'fecha_formateada': cita.fecha.strftime('%d/%m/%Y'),
            'hora_formateada': cita.hora.strftime('%I:%M %p'),
            'nombre_cliente': cita.nombre,
        }
        
        # Email de recordatorio
        html_content = render_to_string('emails/cita_recordatorio.html', context)
        text_content = render_to_string('emails/cita_recordatorio.txt', context)
        
        email_sent = self.email_service.send_email(
            to_email=cita.email,
            subject=f'⏰ Recordatorio de Cita - B&B Car Wash (Mañana {cita.fecha.strftime("%d/%m/%Y")})',
            html_content=html_content,
            text_content=text_content
        )
        
        return {
            'email_sent': email_sent,
            'sms_sent': False,  # SMS deshabilitado
            'cita_id': cita.id
        }
    
    def send_cita_cancelacion(self, cita, motivo=''):
        """Enviar notificación de cancelación"""
        context = {
            'cita': cita,
            'servicio': cita.servicio,
            'fecha_formateada': cita.fecha.strftime('%d/%m/%Y'),
            'hora_formateada': cita.hora.strftime('%I:%M %p'),
            'nombre_cliente': cita.nombre,
            'motivo': motivo
        }
        
        # Email de cancelación
        html_content = render_to_string('emails/cita_cancelacion.html', context)
        text_content = render_to_string('emails/cita_cancelacion.txt', context)
        
        email_sent = self.email_service.send_email(
            to_email=cita.email,
            subject=f'❌ Cita Cancelada - B&B Car Wash ({cita.fecha.strftime("%d/%m/%Y")})',
            html_content=html_content,
            text_content=text_content
        )
        
        return {
            'email_sent': email_sent,
            'sms_sent': False,  # SMS deshabilitado
            'cita_id': cita.id
        }
    
    def send_orden_lista(self, orden):
        """Enviar notificación cuando orden de cafetería está lista"""
        context = {
            'orden': orden,
            'detalles': orden.detalles.all(),
            'total': orden.total,
            'nombre_cliente': orden.cliente_nombre if hasattr(orden, 'cliente_nombre') else 'Cliente'
        }
        
        # Email de orden lista
        html_content = render_to_string('emails/orden_lista.html', context)
        text_content = render_to_string('emails/orden_lista.txt', context)
        
        email_sent = self.email_service.send_email(
            to_email=getattr(orden, 'cliente_email', ''),
            subject=f'☕ Tu Orden de Cafetería Está Lista - B&B Car Wash',
            html_content=html_content,
            text_content=text_content
        )
        
        return {
            'email_sent': email_sent,
            'sms_sent': False,  # SMS deshabilitado
            'orden_id': orden.id
        }
    
    def send_factura_generada(self, factura):
        """Enviar notificación de factura generada"""
        context = {
            'factura': factura,
            'cita': factura.cita,
            'total': factura.total_factura,
            'nombre_cliente': factura.cliente_nombre
        }
        
        # Email de factura
        html_content = render_to_string('emails/factura_generada.html', context)
        text_content = render_to_string('emails/factura_generada.txt', context)
        
        email_sent = self.email_service.send_email(
            to_email=getattr(factura, 'cliente_email', ''),
            subject=f'🧾 Nueva Factura - B&B Car Wash #{factura.numero_factura}',
            html_content=html_content,
            text_content=text_content
        )
        
        return {
            'email_sent': email_sent,
            'sms_sent': False,  # SMS deshabilitado
            'factura_id': factura.id
        }
    
    def send_stock_bajo_alerta(self, producto):
        """Enviar alerta de stock bajo a administradores"""
        context = {
            'producto': producto,
            'stock_actual': producto.stock,
            'nombre_producto': producto.nombre
        }
        
        # Email de alerta de stock
        html_content = render_to_string('emails/stock_bajo_alerta.html', context)
        text_content = render_to_string('emails/stock_bajo_alerta.txt', context)
        
        # Enviar a todos los administradores
        admin_emails = ['admin@bbcarwash.com']  # Configurar emails de admin
        
        email_sent = False
        for admin_email in admin_emails:
            sent = self.email_service.send_email(
                to_email=admin_email,
                subject=f'🚨 Alerta de Stock Bajo - {producto.nombre}',
                html_content=html_content,
                text_content=text_content
            )
            if sent:
                email_sent = True
        
        return {
            'email_sent': email_sent,
            'producto_id': producto.id
        }


class NotificationScheduler:
    """Programador de notificaciones automáticas (solo email)"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def send_recordatorios_diarios(self):
        """Enviar recordatorios de citas (24 horas antes)"""
        manana = datetime.now().date() + timedelta(days=1)
        
        citas_manana = Cita.objects.filter(
            fecha=manana,
            estado__in=['pendiente', 'confirmada']
        )
        
        resultados = []
        for cita in citas_manana:
            resultado = self.notification_service.send_cita_recordatorio(cita)
            resultados.append(resultado)
        
        logger.info(f"Se enviaron {len(resultados)} recordatorios de citas para mañana")
        return resultados
    
    def verificar_stock_bajo(self):
        """Verificar y alertar sobre stock bajo"""
        umbral_bajo = 5
        umbral_critico = 2
        
        productos_bajo = Producto.objects.filter(
            activo=True,
            stock__lte=umbral_bajo
        )
        
        resultados = []
        for producto in productos_bajo:
            if producto.stock <= umbral_critico:
                resultado = self.notification_service.send_stock_bajo_alerta(producto)
                resultados.append(resultado)
        
        logger.info(f"Se enviaron {len(resultados)} alertas de stock crítico")
        return resultados
    
    def enviar_reporte_diario(self):
        """Enviar reporte diario de operaciones"""
        hoy = datetime.now().date()
        
        # Estadísticas del día
        from ..models import Factura, Cita
        
        citas_hoy = Cita.objects.filter(fecha=hoy).count()
        facturas_hoy = Factura.objects.filter(fecha_emision=hoy)
        ingresos_hoy = facturas_hoy.aggregate(total=models.Sum('total_factura'))['total'] or 0
        
        context = {
            'fecha': hoy.strftime('%d/%m/%Y'),
            'citas_count': citas_hoy,
            'facturas_count': facturas_hoy.count(),
            'ingresos_total': ingresos_hoy
        }
        
        # Email de reporte diario
        html_content = render_to_string('emails/reporte_diario.html', context)
        text_content = render_to_string('emails/reporte_diario.txt', context)
        
        notification_service = NotificationService()
        email_sent = notification_service.email_service.send_email(
            to_email='admin@bbcarwash.com',
            subject=f'📊 Reporte Diario - B&B Car Wash ({hoy.strftime("%d/%m/%Y")})',
            html_content=html_content,
            text_content=text_content
        )
        
        logger.info(f"Reporte diario enviado. Ingresos: ${ingresos_hoy}, Citas: {citas_hoy}")
        return {'email_sent': email_sent}
