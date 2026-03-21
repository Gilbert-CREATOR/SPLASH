# carwashapp/context_processors.py

def user_role(request):
    """
    Devuelve el rol del usuario para templates:
    - 'superuser' si es superusuario
    - 'admin' si es staff pero tiene permisos de admin (no superuser)
    - 'empleado' si es staff normal
    - 'cliente' por defecto
    """
    role = "cliente"  # valor por defecto
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = "superuser"
        elif request.user.is_staff and hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin':
            role = "admin"
        elif request.user.is_staff:
            role = "empleado"
    return {'user_role': role}