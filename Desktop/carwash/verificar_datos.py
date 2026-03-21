import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')
django.setup()

from carwashapp.models import Categoria, Producto

print('=== VERIFICANDO DATOS ===')
print(f'Categorías: {Categoria.objects.count()}')
print(f'Productos: {Producto.objects.count()}')

print('\n=== CATEGORÍAS ===')
for cat in Categoria.objects.all():
    print(f'- {cat.nombre} (orden: {cat.orden})')

print('\n=== PRODUCTOS ===')
for prod in Producto.objects.all():
    print(f'- {prod.nombre} ({prod.categoria.nombre}) - ${prod.precio} - Stock: {prod.stock}')
