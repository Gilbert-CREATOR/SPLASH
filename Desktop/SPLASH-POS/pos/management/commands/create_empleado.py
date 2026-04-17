from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create empleado user with emp123 password'

    def handle(self, *args, **options):
        try:
            # Check if user already exists
            if User.objects.filter(username='empleado').exists():
                self.stdout.write(
                    self.style.WARNING('Usuario "empleado" ya existe')
                )
                empleado = User.objects.get(username='empleado')
                self.stdout.write(f"ID: {empleado.id}")
                self.stdout.write(f"Username: {empleado.username}")
                self.stdout.write(f"Email: {empleado.email}")
                self.stdout.write(f"Is Staff: {empleado.is_staff}")
                self.stdout.write(f"Is Active: {empleado.is_active}")
            else:
                # Create the user
                empleado = User.objects.create_user(
                    username='empleado',
                    email='empleado@splashpos.com',
                    password='emp123',
                    first_name='Empleado',
                    last_name='Test',
                    is_staff=False,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS('Usuario "empleado" creado exitosamente')
                )
                self.stdout.write(f"Username: {empleado.username}")
                self.stdout.write(f"Password: emp123")
                self.stdout.write(f"Email: {empleado.email}")
                self.stdout.write(f"Is Staff: {empleado.is_staff}")
                self.stdout.write(f"Is Active: {empleado.is_active}")
            
            # List all users
            self.stdout.write("\n=== Todos los usuarios ===")
            users = User.objects.all().order_by('username')
            for user in users:
                self.stdout.write(f"Username: {user.username}, Staff: {user.is_staff}, Active: {user.is_active}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
