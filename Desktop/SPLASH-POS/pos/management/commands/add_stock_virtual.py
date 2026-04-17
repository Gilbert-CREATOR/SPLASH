from django.core.management.base import BaseCommand
from pos.models import Producto, MovimientoInventario
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add stock_virtual field to existing products'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Adding stock_virtual field to existing products...')
        
        productos = Producto.objects.all()
        count = 0
        
        for producto in productos:
            if not hasattr(producto, 'stock_virtual') or producto.stock_virtual is None:
                producto.stock_virtual = Decimal('0')
                producto.save()
                count += 1
                self.stdout.write(f'✅ Updated: {producto.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Updated {count} products with stock_virtual field')
        )
