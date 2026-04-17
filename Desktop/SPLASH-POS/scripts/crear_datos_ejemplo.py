#!/usr/bin/env python
"""
Script para crear datos de ejemplo en SPLASH POS
Ejecutar: python manage.py shell < scripts/crear_datos_ejemplo.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splash_pos.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth.models import User
from pos.models import Producto, Categoria

def crear_usuario_admin():
    """Crear usuario administrador si no existe"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@splashpos.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print("✅ Usuario admin creado (admin/admin123)")
    else:
        print("ℹ️  Usuario admin ya existe")

def crear_usuario_empleado():
    """Crear usuario empleado si no existe"""
    if not User.objects.filter(username='empleado').exists():
        User.objects.create_user(
            username='empleado',
            email='empleado@splashpos.com',
            password='empleado123',
            first_name='Empleado',
            last_name='Tienda'
        )
        print("✅ Usuario empleado creado (empleado/empleado123)")
    else:
        print("ℹ️  Usuario empleado ya existe")

def crear_categorias():
    """Crear categorías base"""
    categorias_data = [
        'Bebidas',
        'Comidas',
        'Snacks',
        'Lácteos',
        'Panadería',
        'Frutas',
        'Verduras',
        'Carnicería',
        'Abarrotes',
        'Limpieza',
        'Higiene Personal',
        'Electrónica'
    ]
    
    for nombre in categorias_data:
        if not Categoria.objects.filter(nombre=nombre).exists():
            Categoria.objects.create(nombre=nombre)
    
    print("✅ Categorías creadas")

def crear_productos():
    """Crear productos de ejemplo"""
    productos_data = [
        # Bebidas
        {'nombre': 'Coca Cola 600ml', 'categoria': 'Bebidas', 'precio_compra': 35.00, 'precio_venta': 50.00, 'stock': 50},
        {'nombre': 'Pepsi 600ml', 'categoria': 'Bebidas', 'precio_compra': 35.00, 'precio_venta': 50.00, 'stock': 45},
        {'nombre': 'Jugo de Naranja 1L', 'categoria': 'Bebidas', 'precio_compra': 60.00, 'precio_venta': 85.00, 'stock': 30},
        {'nombre': 'Agua Purificada 500ml', 'categoria': 'Bebidas', 'precio_compra': 15.00, 'precio_venta': 25.00, 'stock': 100},
        {'nombre': 'Red Bull 250ml', 'categoria': 'Bebidas', 'precio_compra': 80.00, 'precio_venta': 120.00, 'stock': 20},
        
        # Comidas
        {'nombre': 'Sándwich de Pollo', 'categoria': 'Comidas', 'precio_compra': 80.00, 'precio_venta': 120.00, 'stock': 15},
        {'nombre': 'Hamburguesa Simple', 'categoria': 'Comidas', 'precio_compra': 100.00, 'precio_venta': 150.00, 'stock': 10},
        {'nombre': 'Pizza Personal', 'categoria': 'Comidas', 'precio_compra': 150.00, 'precio_venta': 220.00, 'stock': 8},
        {'nombre': 'Ensalada César', 'categoria': 'Comidas', 'precio_compra': 60.00, 'precio_venta': 95.00, 'stock': 12},
        {'nombre': 'Sopa de Pollo', 'categoria': 'Comidas', 'precio_compra': 40.00, 'precio_venta': 65.00, 'stock': 20},
        
        # Snacks
        {'nombre': 'Papas Fritas 50g', 'categoria': 'Snacks', 'precio_compra': 25.00, 'precio_venta': 40.00, 'stock': 60},
        {'nombre': 'Chocolatina 50g', 'categoria': 'Snacks', 'precio_compra': 30.00, 'precio_venta': 45.00, 'stock': 40},
        {'nombre': 'Galletas Oreo', 'categoria': 'Snacks', 'precio_compra': 35.00, 'precio_venta': 55.00, 'stock': 35},
        {'nombre': 'Cacahuates 100g', 'categoria': 'Snacks', 'precio_compra': 20.00, 'precio_venta': 35.00, 'stock': 50},
        {'nombre': 'Barra de Granola', 'categoria': 'Snacks', 'precio_compra': 25.00, 'precio_venta': 40.00, 'stock': 30},
        
        # Lácteos
        {'nombre': 'Leche 1L', 'categoria': 'Lácteos', 'precio_compra': 55.00, 'precio_venta': 75.00, 'stock': 25},
        {'nombre': 'Queso 500g', 'categoria': 'Lácteos', 'precio_compra': 180.00, 'precio_venta': 250.00, 'stock': 15},
        {'nombre': 'Yogurt Natural 1L', 'categoria': 'Lácteos', 'precio_compra': 70.00, 'precio_venta': 95.00, 'stock': 20},
        {'nombre': 'Mantequilla 250g', 'categoria': 'Lácteos', 'precio_compra': 120.00, 'precio_venta': 165.00, 'stock': 18},
        {'nombre': 'Crema 200ml', 'categoria': 'Lácteos', 'precio_compra': 45.00, 'precio_venta': 65.00, 'stock': 22},
        
        # Panadería
        {'nombre': 'Pan de Molde', 'categoria': 'Panadería', 'precio_compra': 60.00, 'precio_venta': 85.00, 'stock': 20},
        {'nombre': 'Baguette', 'categoria': 'Panadería', 'precio_compra': 25.00, 'precio_venta': 40.00, 'stock': 30},
        {'nombre': 'Croissant', 'categoria': 'Panadería', 'precio_compra': 15.00, 'precio_venta': 25.00, 'stock': 25},
        {'nombre': 'Donas', 'categoria': 'Panadería', 'precio_compra': 20.00, 'precio_venta': 35.00, 'stock': 40},
        {'nombre': 'Pan Integral', 'categoria': 'Panadería', 'precio_compra': 70.00, 'precio_venta': 95.00, 'stock': 15},
        
        # Frutas
        {'nombre': 'Manzanas (kg)', 'categoria': 'Frutas', 'precio_compra': 80.00, 'precio_venta': 120.00, 'stock': 50},
        {'nombre': 'Plátanos (kg)', 'categoria': 'Frutas', 'precio_compra': 45.00, 'precio_venta': 70.00, 'stock': 60},
        {'nombre': 'Naranjas (kg)', 'categoria': 'Frutas', 'precio_compra': 60.00, 'precio_venta': 90.00, 'stock': 40},
        {'nombre': 'Uvas (kg)', 'categoria': 'Frutas', 'precio_compra': 150.00, 'precio_venta': 220.00, 'stock': 20},
        {'nombre': 'Sandía (kg)', 'categoria': 'Frutas', 'precio_compra': 25.00, 'precio_venta': 45.00, 'stock': 30},
        
        # Verduras
        {'nombre': 'Tomates (kg)', 'categoria': 'Verduras', 'precio_compra': 50.00, 'precio_venta': 75.00, 'stock': 35},
        {'nombre': 'Lechuga (unidad)', 'categoria': 'Verduras', 'precio_compra': 20.00, 'precio_venta': 35.00, 'stock': 25},
        {'nombre': 'Cebollas (kg)', 'categoria': 'Verduras', 'precio_compra': 40.00, 'precio_venta': 65.00, 'stock': 45},
        {'nombre': 'Pimientos (kg)', 'categoria': 'Verduras', 'precio_compra': 70.00, 'precio_venta': 110.00, 'stock': 20},
        {'nombre': 'Zanahorias (kg)', 'categoria': 'Verduras', 'precio_compra': 35.00, 'precio_venta': 55.00, 'stock': 40},
        
        # Carnicería
        {'nombre': 'Pollo (kg)', 'categoria': 'Carnicería', 'precio_compra': 150.00, 'precio_venta': 220.00, 'stock': 30},
        {'nombre': 'Carne de Res (kg)', 'categoria': 'Carnicería', 'precio_compra': 350.00, 'precio_venta': 480.00, 'stock': 15},
        {'nombre': 'Cerdo (kg)', 'categoria': 'Carnicería', 'precio_compra': 280.00, 'precio_venta': 380.00, 'stock': 20},
        {'nombre': 'Salchichas (paquete)', 'categoria': 'Carnicería', 'precio_compra': 120.00, 'precio_venta': 180.00, 'stock': 25},
        {'nombre': 'Jamón (kg)', 'categoria': 'Carnicería', 'precio_compra': 450.00, 'precio_venta': 620.00, 'stock': 10},
        
        # Abarrotes
        {'nombre': 'Arroz (kg)', 'categoria': 'Abarrotes', 'precio_compra': 40.00, 'precio_venta': 60.00, 'stock': 100},
        {'nombre': 'Frijoles (kg)', 'categoria': 'Abarrotes', 'precio_compra': 65.00, 'precio_venta': 90.00, 'stock': 80},
        {'nombre': 'Azúcar (kg)', 'categoria': 'Abarrotes', 'precio_compra': 45.00, 'precio_venta': 65.00, 'stock': 90},
        {'nombre': 'Sal (kg)', 'categoria': 'Abarrotes', 'precio_compra': 15.00, 'precio_venta': 25.00, 'stock': 120},
        {'nombre': 'Aceite 900ml', 'categoria': 'Abarrotes', 'precio_compra': 85.00, 'precio_venta': 120.00, 'stock': 40},
        
        # Limpieza
        {'nombre': 'Cloro 1L', 'categoria': 'Limpieza', 'precio_compra': 30.00, 'precio_venta': 50.00, 'stock': 35},
        {'nombre': 'Detergente 500ml', 'categoria': 'Limpieza', 'precio_compra': 45.00, 'precio_venta': 70.00, 'stock': 30},
        {'nombre': 'Jabón Líquido 250ml', 'categoria': 'Limpieza', 'precio_compra': 35.00, 'precio_venta': 55.00, 'stock': 40},
        {'nombre': 'Limpiavidrios 500ml', 'categoria': 'Limpieza', 'precio_compra': 40.00, 'precio_venta': 65.00, 'stock': 25},
        {'nombre': 'Desinfectante 1L', 'categoria': 'Limpieza', 'precio_compra': 60.00, 'precio_venta': 85.00, 'stock': 20},
        
        # Higiene Personal
        {'nombre': 'Pasta Dental 100ml', 'categoria': 'Higiene Personal', 'precio_compra': 55.00, 'precio_venta': 80.00, 'stock': 30},
        {'nombre': 'Jabón de Tocador', 'categoria': 'Higiene Personal', 'precio_compra': 25.00, 'precio_venta': 40.00, 'stock': 50},
        {'nombre': 'Shampoo 400ml', 'categoria': 'Higiene Personal', 'precio_compra': 85.00, 'precio_venta': 125.00, 'stock': 25},
        {'nombre': 'Desodorante 90g', 'categoria': 'Higiene Personal', 'precio_compra': 70.00, 'precio_venta': 100.00, 'stock': 35},
        {'nombre': 'Papel Higiénico (rollo)', 'categoria': 'Higiene Personal', 'precio_compra': 20.00, 'precio_venta': 35.00, 'stock': 60},
        
        # Electrónica
        {'nombre': 'Pilaa AA', 'categoria': 'Electrónica', 'precio_compra': 15.00, 'precio_venta': 25.00, 'stock': 100},
        {'nombre': 'Pilaa AAA', 'categoria': 'Electrónica', 'precio_compra': 15.00, 'precio_venta': 25.00, 'stock': 100},
        {'nombre': 'Cargador USB', 'categoria': 'Electrónica', 'precio_compra': 150.00, 'precio_venta': 250.00, 'stock': 20},
        {'nombre': 'Audífonos Básicos', 'categoria': 'Electrónica', 'precio_compra': 200.00, 'precio_venta': 350.00, 'stock': 15},
        {'nombre': 'Mouse USB', 'categoria': 'Electrónica', 'precio_compra': 250.00, 'precio_venta': 400.00, 'stock': 10},
    ]
    
    productos_creados = 0
    for producto_data in productos_data:
        if not Producto.objects.filter(nombre=producto_data['nombre']).exists():
            Producto.objects.create(
                nombre=producto_data['nombre'],
                categoria=producto_data['categoria'],
                precio_compra=Decimal(str(producto_data['precio_compra'])),
                precio_venta=Decimal(str(producto_data['precio_venta'])),
                stock=Decimal(str(producto_data['stock']))
            )
            productos_creados += 1
    
    print(f"✅ {productos_creados} productos creados")

def main():
    """Función principal"""
    print("🚀 Creando datos de ejemplo para SPLASH POS")
    print("=" * 50)
    
    crear_usuario_admin()
    crear_usuario_empleado()
    crear_categorias()
    crear_productos()
    
    print("=" * 50)
    print("✅ Datos de ejemplo creados exitosamente")
    print("\n📋 Usuarios creados:")
    print("   Admin: admin/admin123")
    print("   Empleado: empleado/empleado123")
    print("\n🏪 Productos creados por categoría:")
    
    for categoria in Categoria.objects.all().order_by('nombre'):
        count = Producto.objects.filter(categoria=categoria.nombre).count()
        print(f"   {categoria.nombre}: {count} productos")
    
    print(f"\n📦 Total productos: {Producto.objects.count()}")
    print("\n🎯 El sistema está listo para usar!")
    print("   Ejecuta: python manage.py runserver")
    print("   Y visita: http://127.0.0.1:8000")

if __name__ == '__main__':
    main()
