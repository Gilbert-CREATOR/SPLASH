from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_virtual = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Stock reservado para ventas
    ventas_pendientes = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Ventas sin stock disponible
    categoria = models.CharField(max_length=100, default='General')
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - RD$ {self.precio_venta}"

    @property
    def ganancia_unitaria(self):
        return self.precio_venta - self.precio_compra

    @property
    def margen_porcentaje(self):
        if self.precio_venta > 0:
            return (self.ganancia_unitaria / self.precio_venta) * 100
        return 0

    @property
    def stock_disponible(self):
        """Stock disponible para venta (stock_real - stock_virtual)"""
        return max(Decimal('0'), self.stock - self.stock_virtual)

    @property
    def stock_real_disponible(self):
        """Stock real disponible para mostrar al cliente"""
        stock_real = self.stock - self.ventas_pendientes
        return max(Decimal('0'), stock_real)


class Venta(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]

    numero_venta = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    dinero_recibido = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cambio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    nota = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cancelada = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta {self.numero_venta} - RD$ {self.total}"

    @property
    def ganancia_total(self):
        total_ganancia = Decimal('0.00')
        for detalle in self.detalles.all():
            ganancia_unitaria = detalle.precio_unitario - detalle.producto.precio_compra
            total_ganancia += ganancia_unitaria * detalle.cantidad
        return total_ganancia

    def save(self, *args, **kwargs):
        if not self.numero_venta:
            ultima_venta = Venta.objects.all().order_by('-id').first()
            if ultima_venta:
                ultimo_numero = int(ultima_venta.numero_venta.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            self.numero_venta = f"V-{nuevo_numero:06d}"
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class MovimientoInventario(models.Model):
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.title()} de {self.producto.nombre}: {self.cantidad}"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
