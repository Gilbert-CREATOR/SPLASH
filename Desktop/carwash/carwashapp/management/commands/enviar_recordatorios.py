from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from carwashapp.models import Cita
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Enviar recordatorios de citas 1 hora y 30 minutos antes"

    def handle(self, *args, **kwargs):

        ahora = timezone.now()

        citas = Cita.objects.filter(
            recordatorio_enviado=False
        )

        for cita in citas:
            try:

                hora_cita = cita.hora

                # Si la hora viene como texto
                if isinstance(hora_cita, str):
                    hora_cita = datetime.strptime(hora_cita, "%H:%M").time()

                # Combinar fecha y hora
                fecha_hora_cita = datetime.combine(cita.fecha, hora_cita)

                # Diferencia entre ahora y la cita
                diferencia = fecha_hora_cita - ahora.replace(tzinfo=None)

                # Si faltan entre 1h29 y 1h31
                if timedelta(hours=1, minutes=29) <= diferencia <= timedelta(hours=1, minutes=31):

                    if cita.email:

                        send_mail(
                            "Recordatorio de cita - Car Wash",
                            f"""
Hola {cita.nombre},

Este es un recordatorio de que tu cita para el servicio
"{cita.servicio}" es hoy a las {hora_cita}.

Te esperamos.

Car Wash
""",
                            "tu_correo@gmail.com",
                            [cita.email],
                            fail_silently=False,
                        )

                        cita.recordatorio_enviado = True
                        cita.save()

                        print(f"Recordatorio enviado a {cita.nombre}")

            except Exception as e:
                print(f"Error procesando cita {cita.id}: {e}")