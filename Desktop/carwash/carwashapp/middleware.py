from django.utils import timezone
from .models import SesionEmpleado

class SesionEmpleadoMiddleware:
    """
    Middleware para tracking de sesiones de empleados
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Procesar la solicitud
        response = self.get_response(request)
        
        # Solo procesar para usuarios autenticados que son staff
        if request.user.is_authenticated and request.user.is_staff:
            self._registrar_sesion(request)
        
        return response
    
    def _registrar_sesion(self, request):
        """
        Registra o actualiza la sesión del empleado
        """
        # Buscar sesión activa del empleado
        sesion_activa = SesionEmpleado.objects.filter(
            empleado=request.user,
            activa=True
        ).first()
        
        if not sesion_activa:
            # Crear nueva sesión
            SesionEmpleado.objects.create(
                empleado=request.user,
                fecha_inicio=timezone.now()
            )
        
        # Finalizar sesiones antiguas (más de 24 horas)
        SesionEmpleado.objects.filter(
            activa=True,
            fecha_inicio__lt=timezone.now() - timezone.timedelta(hours=24)
        ).update(
            activa=False,
            fecha_fin=timezone.now()
        )
