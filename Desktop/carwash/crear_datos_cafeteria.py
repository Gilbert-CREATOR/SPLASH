#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')
django.setup()

from carwashapp.models import Categoria, Producto

def crear_datos_ejemplo():
    print("🍽️ Creando datos de ejemplo para la cafetería...")
    
    # Crear categorías
    categorias_data = [
        {'nombre': 'Bebidas Calientes', 'descripcion': 'Café, té y otras bebidas calientes', 'orden': 1},
        {'nombre': 'Bebidas Frías', 'descripcion': 'Refrescos, jugos y bebidas frías', 'orden': 2},
        {'nombre': 'Snacks', 'descripcion': 'Comidas ligeras y snacks', 'orden': 3},
        {'nombre': 'Postres', 'descripcion': 'Postres caseros y dulces', 'orden': 4},
    ]
    
    for cat_data in categorias_data:
        categoria, created = Categoria.objects.get_or_create(**cat_data)
        print(f"✅ Categoría '{categoria.nombre}': {'creada' if created else 'ya existía'}")
    
    # Crear productos
    productos_data = [
        {
            'categoria': Categoria.objects.get(nombre='Bebidas Calientes'),
            'nombre': 'Café Americano',
            'descripcion': 'Café recién hecho, 100% arábica',
            'precio': 2.50,
            'stock': 50,
            'popular': True,
            'preparacion_tiempo': 5,
            'ingredientes': 'Café, agua'
        },
        {
            'categoria': Categoria.objects.get(nombre='Bebidas Calientes'),
            'nombre': 'Capuchino',
            'descripcion': 'Café con leche espumosa y canela',
            'precio': 3.50,
            'stock': 30,
            'popular': True,
            'preparacion_tiempo': 7,
            'ingredientes': 'Café, leche espumosa, canela'
        },
        {
            'categoria': Categoria.objects.get(nombre='Bebidas Calientes'),
            'nombre': 'Té Verde',
            'descripcion': 'Té verde japonés, antioxidante',
            'precio': 2.00,
            'stock': 40,
            'popular': False,
            'preparacion_tiempo': 3,
            'ingredientes': 'Té verde, agua caliente'
        },
        {
            'categoria': Categoria.objects.get(nombre='Bebidas Frías'),
            'nombre': 'Refresco de Cola',
            'descripcion': 'Refresco cola tradicional, bien frío',
            'precio': 1.50,
            'stock': 40,
            'popular': False,
            'preparacion_tiempo': 1,
            'ingredientes': 'Agua carbonatada, azúcar, cafeína'
        },
        {
            'categoria': Categoria.objects.get(nombre='Bebidas Frías'),
            'nombre': 'Jugo de Naranja',
            'descripcion': 'Jugo de naranja natural 100%',
            'precio': 2.50,
            'stock': 25,
            'popular': True,
            'preparacion_tiempo': 2,
            'ingredientes': 'Naranja, hielo'
        },
        {
            'categoria': Categoria.objects.get(nombre='Snacks'),
            'nombre': 'Sandwich de Jamón',
            'descripcion': 'Sandwich con jamón, queso y lechuga',
            'precio': 4.00,
            'stock': 15,
            'popular': True,
            'preparacion_tiempo': 8,
            'ingredientes': 'Pan, jamón, queso, lechuga, tomate'
        },
        {
            'categoria': Categoria.objects.get(nombre='Snacks'),
            'nombre': 'Papas Fritas',
            'descripcion': 'Papas fritas crujientes con sal',
            'precio': 2.00,
            'stock': 25,
            'popular': False,
            'preparacion_tiempo': 5,
            'ingredientes': 'Papas, sal, aceite'
        },
        {
            'categoria': Categoria.objects.get(nombre='Snacks'),
            'nombre': 'Ensalada César',
            'descripcion': 'Ensalada fresca con pollo y aderezo césar',
            'precio': 5.50,
            'stock': 10,
            'popular': False,
            'preparacion_tiempo': 10,
            'ingredientes': 'Lechuga, pollo, parmesano, crutones, aderezo césar'
        },
        {
            'categoria': Categoria.objects.get(nombre='Postres'),
            'nombre': 'Pastel de Chocolate',
            'descripcion': 'Pastel de chocolate casero con crema',
            'precio': 3.00,
            'stock': 10,
            'popular': True,
            'preparacion_tiempo': 2,
            'ingredientes': 'Chocolate, harina, huevos, crema'
        },
        {
            'categoria': Categoria.objects.get(nombre='Postres'),
            'nombre': 'Flan de Vainilla',
            'descripcion': 'Flan cremoso con caramelo',
            'precio': 2.50,
            'stock': 12,
            'popular': False,
            'preparacion_tiempo': 2,
            'ingredientes': 'Huevos, leche, vainilla, caramelo'
        },
    ]
    
    for prod_data in productos_data:
        producto, created = Producto.objects.get_or_create(
            nombre=prod_data['nombre'],
            categoria=prod_data['categoria'],
            defaults={
                'descripcion': prod_data['descripcion'],
                'precio': prod_data['precio'],
                'stock': prod_data['stock'],
                'popular': prod_data['popular'],
                'preparacion_tiempo': prod_data['preparacion_tiempo'],
                'ingredientes': prod_data['ingredientes']
            }
        )
        print(f"✅ Producto '{producto.nombre}': {'creado' if created else 'ya existía'}")
    
    print("\n🎉 ¡Datos de ejemplo creados exitosamente!")
    print(f"📊 Total categorías: {Categoria.objects.count()}")
    print(f"🍽️ Total productos: {Producto.objects.count()}")

if __name__ == '__main__':
    crear_datos_ejemplo()
