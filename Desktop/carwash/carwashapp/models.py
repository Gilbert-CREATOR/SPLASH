from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ==========================
# MODELO MARCA
# ==========================
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================
# MODELO MODELO
# ==========================
class Modelo(models.Model):
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        related_name='modelos'
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['nombre']
        unique_together = ('marca', 'nombre')

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"


# ==========================
# MODELO SERVICIO
# ==========================
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# ==========================
# MODELO CITA
# ==========================
class Cita(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True, null=True)

    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.ForeignKey(Modelo, on_delete=models.SET_NULL, null=True, blank=True)

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()

    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('en_proceso', 'En Proceso'),
            ('cancelada', 'Cancelada'),
            ('finalizada', 'Finalizada'),
        ],
        default='pendiente'
    )

    # Empleado que agendó la cita (si fue por panel)
    agendado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_agendadas'
    )

    correo_enviado = models.BooleanField(default=False)

    # Recordatorio enviado
    recordatorio_enviado = models.BooleanField(default=False)

    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.marca and self.modelo:
            return f"{self.nombre} - {self.marca} {self.modelo.nombre}"
        return f"{self.nombre} - {self.fecha} {self.hora}"

    # 🔹 VALIDACIÓN PARA EVITAR CITAS DUPLICADAS
    def clean(self):
        if Cita.objects.filter(fecha=self.fecha, hora=self.hora).exclude(id=self.id).exists():
            raise ValidationError("Ya existe una cita reservada en este horario.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # Métodos para templates
    def puede_finalizar(self):
        return self.estado in ['confirmada', 'en_proceso']

    def puede_cancelar(self):
        return self.estado != 'finalizada'

    def puede_confirmar(self):
        return self.estado == 'pendiente'

    def puede_en_proceso(self):
        return self.estado == 'confirmada'


# ==========================
# MODELO VEHICULO
# ==========================
class Vehiculo(models.Model):
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.marca.nombre} {self.modelo.nombre}"


# ==========================
# PERFIL DE EMPLEADO
# ==========================
class perfil(models.Model):
    ROL_CHOICES = [
        ('empleado', 'Empleado'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_contratacion = models.DateField(default=timezone.now)
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='empleado')

    def __str__(self):
        return f"{self.nombre} ({self.get_rol_display()})"


# ==========================
# SISTEMA DE CAFETERÍA Y FACTURACIÓN
# ==========================

class Categoria(models.Model):
    """Categorías de productos de la cafetería"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Productos de la cafetería"""
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='productos'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(
        upload_to='cafeteria/productos/', 
        blank=True, 
        null=True
    )
    activo = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    preparacion_tiempo = models.PositiveIntegerField(
        default=5, 
        help_text="Tiempo de preparación en minutos"
    )
    stock = models.PositiveIntegerField(default=0)
    ingredientes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Ingredientes o alérgenos"
    )

    class Meta:
        ordering = ['categoria', 'nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    @property
    def disponible(self):
        return self.activo and self.stock > 0


class SesionEmpleado(models.Model):
    """Registro de sesiones de empleados"""
    empleado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sesiones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    duracion_segundos = models.PositiveIntegerField(null=True, blank=True, help_text="Duración en segundos")
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Sesión de Empleado'
        verbose_name_plural = 'Sesiones de Empleados'
    
    def __str__(self):
        return f"Sesión de {self.empleado.username} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duracion_formateada(self):
        """Devuelve la duración formateada (ej: 2h 30m)"""
        if not self.duracion_segundos:
            return "Activa"
        
        horas = self.duracion_segundos // 3600
        minutos = (self.duracion_segundos % 3600) // 60
        
        if horas > 0 and minutos > 0:
            return f"{horas}h {minutos}m"
        elif horas > 0:
            return f"{horas}h"
        else:
            return f"{minutos}m"
    
    def finalizar_sesion(self):
        """Finaliza la sesión y calcula la duración"""
        from django.utils import timezone
        if self.activa:
            self.fecha_fin = timezone.now()
            if self.fecha_inicio:
                delta = self.fecha_fin - self.fecha_inicio
                self.duracion_segundos = int(delta.total_seconds())
            self.activa = False
            self.save()


class OrdenCafeteria(models.Model):
    """Órdenes de la cafetería"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo para Entregar'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True)
    cita = models.ForeignKey(
        Cita, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_cafeteria'
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente'
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    hora_entrega_estimada = models.DateTimeField(null=True, blank=True)
    entregado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_entregadas'
    )

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Orden de Cafetería'
        verbose_name_plural = 'Órdenes de Cafetería'

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente_nombre}"

    def calcular_totales(self):
        """Calcular subtotal, impuesto y total"""
        subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
        impuesto = subtotal * 0.16  # 16% ITBIS
        total = subtotal + impuesto
        
        self.subtotal = subtotal
        self.impuesto = impuesto
        self.total = total
        self.save()

    @property
    def cantidad_items(self):
        return sum(detalle.cantidad for detalle in self.detalles.all())


class DetalleOrden(models.Model):
    """Detalles de cada orden"""
    orden = models.ForeignKey(
        OrdenCafeteria, 
        on_delete=models.CASCADE, 
        related_name='detalles'
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Detalle de Orden'
        verbose_name_plural = 'Detalles de Orden'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class Factura(models.Model):
    """Factura unificada (servicios + cafetería)"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('emitida', 'Emitida'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
    ]

    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('mixto', 'Mixto'),
    ]

    numero_factura = models.CharField(max_length=20, unique=True)
    cita = models.OneToOneField(
        Cita, 
        on_delete=models.CASCADE, 
        related_name='factura'
    )
    orden_cafeteria = models.OneToOneField(
        OrdenCafeteria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='factura'
    )
    
    # Desglose de costos
    subtotal_servicios = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_cafeteria = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Impuestos
    impuesto_servicios = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto_cafeteria = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Total final
    total_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Información de pago
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODOS_PAGO, 
        default='efectivo'
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente'
    )
    
    # Fechas
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20)
    cliente_email = models.EmailField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    # Quién emitió la factura
    emitida_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='facturas_emitidas'
    )

    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f"Factura #{self.numero_factura} - {self.cliente_nombre}"

    def generar_numero_factura(self):
        """Generar número de factura único"""
        from django.utils import timezone
        import uuid
        
        fecha_actual = timezone.now().strftime('%Y%m%d')
        aleatorio = str(uuid.uuid4())[:8].upper()
        self.numero_factura = f"F-{fecha_actual}-{aleatorio}"
        self.save()

    def calcular_totales(self):
        """Calcular todos los totales de la factura"""
        # Subtotal servicios
        if self.cita and self.cita.servicio:
            self.subtotal_servicios = self.cita.servicio.precio
        else:
            self.subtotal_servicios = 0
            
        # Subtotal cafetería
        if self.orden_cafeteria:
            self.subtotal_cafeteria = self.orden_cafeteria.subtotal
        else:
            self.subtotal_cafeteria = 0
            
        # Subtotal total
        self.subtotal_total = self.subtotal_servicios + self.subtotal_cafeteria
        
        # Impuestos (16% para ambos conceptos)
        self.impuesto_servicios = self.subtotal_servicios * 0.16
        self.impuesto_cafeteria = self.subtotal_cafeteria * 0.16
        self.impuesto_total = self.impuesto_servicios + self.impuesto_cafeteria
        
        # Total final
        self.total_factura = self.subtotal_total + self.impuesto_total
        self.save()

    @property
    def tiene_cafeteria(self):
        return self.orden_cafeteria is not None

    @property
    def esta_pagada(self):
        return self.estado == 'pagada'