from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from pos.models import Producto, Venta, MovimientoInventario
import os

class Command(BaseCommand):
    help = 'Optimize database performance and integrity'

    def handle(self, *args, **options):
        self.stdout.write('🗄️ DATABASE OPTIMIZATION')
        self.stdout.write('=' * 40)
        
        try:
            # Check database integrity
            self.stdout.write('🔍 Checking database integrity...')
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result[0] == 'ok':
                    self.stdout.write(self.style.SUCCESS('✅ Database integrity check passed'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Database integrity issues: {result[0]}'))
                    return
            
            # Analyze database statistics
            self.stdout.write('📊 Analyzing database statistics...')
            with connection.cursor() as cursor:
                cursor.execute("ANALYZE")
                self.stdout.write(self.style.SUCCESS('✅ Database statistics updated'))
            
            # Vacuum database
            self.stdout.write('🧹 Vacuuming database...')
            with connection.cursor() as cursor:
                cursor.execute("VACUUM")
                self.stdout.write(self.style.SUCCESS('✅ Database vacuum completed'))
            
            # Check database size
            db_path = connection.settings_dict['NAME']
            if os.path.exists(db_path):
                original_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
                self.stdout.write(f'📏 Database size: {original_size:.2f} MB')
            
            # Check table statistics
            self.stdout.write('📋 Table statistics:')
            with connection.cursor() as cursor:
                tables = [
                    ('auth_user', 'Users'),
                    ('pos_producto', 'Products'),
                    ('pos_venta', 'Sales'),
                    ('pos_movimiento inventario', 'Inventory Movements')
                ]
                
                for table_name, display_name in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        self.stdout.write(f'   📊 {display_name}: {count} records')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'   ⚠️  Could not get stats for {display_name}: {e}'))
            
            # Check for orphaned records
            self.stdout.write('🔍 Checking for orphaned records...')
            
            # Check for sales without valid products
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT COUNT(*) FROM pos_venta v 
                    LEFT JOIN pos_producto p ON v.producto_id = p.id 
                    WHERE p.id IS NULL
                ''')
                orphaned_sales = cursor.fetchone()[0]
                if orphaned_sales > 0:
                    self.stdout.write(self.style.WARNING(f'⚠️  Found {orphaned_sales} orphaned sales records'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ No orphaned sales records found'))
            
            # Check for inventory movements without valid products
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT COUNT(*) FROM pos_movimiento inventario m 
                    LEFT JOIN pos_producto p ON m.producto_id = p.id 
                    WHERE p.id IS NULL
                ''')
                orphaned_movements = cursor.fetchone()[0]
                if orphaned_movements > 0:
                    self.stdout.write(self.style.WARNING(f'⚠️  Found {orphaned_movements} orphaned inventory movements'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ No orphaned inventory movements found'))
            
            # Optimize indexes
            self.stdout.write('⚡ Optimizing indexes...')
            with connection.cursor() as cursor:
                # Create indexes for common queries
                indexes = [
                    'CREATE INDEX IF NOT EXISTS idx_producto_categoria ON pos_producto(categoria)',
                    'CREATE INDEX IF NOT EXISTS idx_producto_activo ON pos_producto(activo)',
                    'CREATE INDEX IF NOT EXISTS idx_venta_fecha ON pos_venta(fecha)',
                    'CREATE INDEX IF NOT EXISTS idx_movimiento_fecha ON pos_movimiento inventario(fecha)',
                    'CREATE INDEX IF NOT EXISTS idx_user_username ON auth_user(username)',
                ]
                
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                        self.stdout.write(self.style.SUCCESS(f'✅ Created index'))
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            self.stdout.write(self.style.WARNING(f'⚠️  Index creation warning: {e}'))
            
            # Check final database size
            if os.path.exists(db_path):
                final_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
                if 'original_size' in locals():
                    size_change = final_size - original_size
                    if size_change < 0:
                        self.stdout.write(self.style.SUCCESS(f'📏 Database optimized: saved {abs(size_change):.2f} MB'))
                    else:
                        self.stdout.write(self.style.WARNING(f'📏 Database size increased: {size_change:.2f} MB'))
                self.stdout.write(f'📏 Final database size: {final_size:.2f} MB')
            
            # Performance recommendations
            self.stdout.write('\n💡 PERFORMANCE RECOMMENDATIONS:')
            
            # Check user count
            user_count = User.objects.count()
            if user_count > 100:
                self.stdout.write('   • Consider archiving inactive users')
            
            # Check product count
            product_count = Producto.objects.count()
            if product_count > 1000:
                self.stdout.write('   • Consider product categorization for better performance')
            
            # Check sales count
            sales_count = Venta.objects.count()
            if sales_count > 10000:
                self.stdout.write('   • Consider archiving old sales records')
            
            # General recommendations
            self.stdout.write('   • Run optimization weekly')
            self.stdout.write('   • Monitor database growth')
            self.stdout.write('   • Keep regular backups')
            self.stdout.write('   • Archive old data periodically')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Database optimization completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database optimization failed: {e}'))
            import traceback
            traceback.print_exc()
