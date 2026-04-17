from django.contrib import admin
from .models import Categoria, Producto, Venta, DetalleVenta, MovimientoInventario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'created_at']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_venta', 'stock', 'activo', 'created_at']
    list_filter = ['categoria', 'activo', 'created_at']
    search_fields = ['nombre', 'categoria']
    list_editable = ['activo']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'activo')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta')
        }),
        ('Inventario', {
            'fields': ('stock',)
        }),
        ('Información Adicional', {
            'fields': ('codigo_barras',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    can_delete = False


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['numero_venta', 'fecha', 'usuario', 'total', 'metodo_pago', 'cancelada']
    list_filter = ['metodo_pago', 'cancelada', 'fecha', 'usuario']
    search_fields = ['numero_venta', 'usuario__username']
    readonly_fields = ['numero_venta', 'fecha', 'created_at']
    inlines = [DetalleVentaInline]
    ordering = ['-fecha']
    
    fieldsets = (
        ('Información de Venta', {
            'fields': ('numero_venta', 'fecha', 'usuario')
        }),
        ('Detalles Financieros', {
            'fields': ('total', 'metodo_pago', 'dinero_recibido', 'cambio')
        }),
        ('Información Adicional', {
            'fields': ('nota', 'cancelada')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si el objeto ya existe
            return self.readonly_fields + ['total', 'metodo_pago']
        return self.readonly_fields


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha', 'producto__categoria']
    search_fields = ['venta__numero_venta', 'producto__nombre']
    readonly_fields = ['subtotal']
    ordering = ['-venta__fecha']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si el objeto ya existe
            return self.readonly_fields + ['venta', 'producto', 'cantidad', 'precio_unitario']
        return self.readonly_fields


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha']
    list_filter = ['tipo', 'fecha', 'usuario']
    search_fields = ['producto__nombre', 'motivo', 'usuario__username']
    readonly_fields = ['stock_anterior', 'stock_nuevo', 'fecha']
    ordering = ['-fecha']
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('producto', 'tipo', 'cantidad')
        }),
        ('Stock', {
            'fields': ('stock_anterior', 'stock_nuevo')
        }),
        ('Información Adicional', {
            'fields': ('motivo', 'usuario')
        }),
    )
