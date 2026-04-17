from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from decimal import Decimal
import json
from datetime import datetime, timedelta
from .models import Producto, Venta, DetalleVenta, MovimientoInventario, Categoria


def login_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('pos')
    return redirect('login')


@login_required
def dashboard(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    # Obtener fecha actual en zona horaria local
    from django.utils import timezone
    hoy = timezone.localtime(timezone.now()).date()
    
    ventas_hoy = Venta.objects.filter(fecha__date=hoy, cancelada=False)
    
    # Estadísticas del día
    total_ventas_hoy = ventas_hoy.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    numero_ventas_hoy = ventas_hoy.count()
    
    # Ganancias del día
    ganancias_hoy = Decimal('0.00')
    for venta in ventas_hoy:
        ganancias_hoy += venta.ganancia_total
    
    # Productos más vendidos
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__cancelada=False
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    # Ventas recientes
    ventas_recientes = Venta.objects.filter(cancelada=False).order_by('-fecha')[:10]
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(stock__lt=10, activo=True).order_by('stock')[:10]
    
    context = {
        'total_ventas_hoy': total_ventas_hoy,
        'numero_ventas_hoy': numero_ventas_hoy,
        'ganancias_hoy': ganancias_hoy,
        'productos_mas_vendidos': productos_mas_vendidos,
        'ventas_recientes': ventas_recientes,
        'productos_stock_bajo': productos_stock_bajo,
    }
    
    return render(request, 'dashboard_simple.html', context)


@login_required
def pos_view(request):
    # El POS está disponible para todos los usuarios autenticados
    # No hay redirección basada en is_staff
    
    productos = Producto.objects.filter(activo=True).order_by('categoria', 'nombre')
    # Mostrar TODAS las categorías en los botones del POS
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    # Top productos del día
    hoy = timezone.now().date()
    top_productos = DetalleVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__cancelada=False
    ).values('producto__id', 'producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'top_productos': top_productos,
    }
    
    return render(request, 'pos.html', context)


@login_required
def historial_ventas(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    filtro = request.GET.get('filtro', 'hoy')
    hoy = timezone.now().date()
    
    if filtro == 'hoy':
        ventas = Venta.objects.filter(fecha__date=hoy, cancelada=False)
    elif filtro == 'ayer':
        ayer = hoy - timedelta(days=1)
        ventas = Venta.objects.filter(fecha__date=ayer, cancelada=False)
    elif filtro == 'semana':
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        ventas = Venta.objects.filter(fecha__date__gte=semana_inicio, cancelada=False)
    else:
        ventas = Venta.objects.filter(cancelada=False)
    
    ventas = ventas.order_by('-fecha')
    
    context = {
        'ventas': ventas,
        'filtro_actual': filtro,
    }
    
    return render(request, 'historial_ventas.html', context)


@login_required
def detalle_venta(request, venta_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    
    return render(request, 'detalle_venta.html', context)


@login_required
def gestion_productos(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    # Calcular conteos para el template
    total_productos = productos.count()
    productos_activos = productos.filter(activo=True).count()
    productos_inactivos = productos.filter(activo=False).count()
    valor_inventario = sum(p.stock * p.precio_venta for p in productos)
    productos_stock_bajo = productos.filter(stock__lt=10, activo=True).order_by('stock')[:10]
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_inactivos': productos_inactivos,
        'valor_inventario': valor_inventario,
        'productos_stock_bajo': productos_stock_bajo,
    }
    
    return render(request, 'gestion_productos_simple.html', context)


@login_required
def nuevo_producto(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio_compra = Decimal(request.POST.get('precio_compra'))
        precio_venta = Decimal(request.POST.get('precio_venta'))
        stock = Decimal(request.POST.get('stock'))
        
        # Manejar categoría
        categoria_seleccionada = request.POST.get('categoria')
        nueva_categoria = request.POST.get('nueva_categoria')
        
        if nueva_categoria and nueva_categoria.strip():
            # Se creó una nueva categoría
            categoria = nueva_categoria.strip()
        elif categoria_seleccionada:
            # Se seleccionó una categoría existente
            categoria = categoria_seleccionada
        else:
            # Por defecto
            categoria = 'General'
        
        Producto.objects.create(
            nombre=nombre,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock=stock,
            stock_virtual=0,  # Inicializar en 0
            ventas_pendientes=0,  # Inicializar en 0
            categoria=categoria
        )
        
        return redirect('gestion_productos')
    
    # Obtener TODAS las categorías existentes (incluyendo las que no tienen productos activos)
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'nuevo_producto.html', context)


@login_required
def editar_producto(request, producto_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio_compra = Decimal(request.POST.get('precio_compra'))
        producto.precio_venta = Decimal(request.POST.get('precio_venta'))
        producto.stock = Decimal(request.POST.get('stock'))
        producto.categoria = request.POST.get('categoria', 'General')
        producto.activo = 'activo' in request.POST
        producto.save()
        
        return redirect('gestion_productos')
    
    # Obtener TODAS las categorías existentes (incluyendo las que no tienen productos activos)
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    context = {
        'producto': producto,
        'categorias': categorias,
    }
    
    return render(request, 'editar_producto.html', context)


@login_required
def eliminar_producto(request, producto_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    
    return redirect('gestion_productos')


@login_required
@csrf_exempt
@require_POST
def procesar_venta(request):
    try:
        data = json.loads(request.body)
        carrito = data.get('carrito', [])
        metodo_pago = data.get('metodo_pago')
        dinero_recibido = Decimal(data.get('dinero_recibido', '0'))
        nota = data.get('nota', '')
        
        if not carrito:
            return JsonResponse({'success': False, 'error': 'El carrito está vacío'})
        
        # Calcular total
        total = Decimal('0.00')
        for item in carrito:
            total += Decimal(str(item['precio'])) * Decimal(str(item['cantidad']))
        
        # Crear venta
        venta = Venta.objects.create(
            total=total,
            metodo_pago=metodo_pago,
            dinero_recibido=dinero_recibido if metodo_pago == 'efectivo' else None,
            cambio=dinero_recibido - total if metodo_pago == 'efectivo' else None,
            nota=nota,
            usuario=request.user
        )
        
        # Crear detalles y actualizar stock
        for item in carrito:
            producto = Producto.objects.get(id=item['id'])
            cantidad = Decimal(str(item['cantidad']))
            
            # NO VERIFICAR STOCK - Permitir vender sin límite
            
            # Crear detalle
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=Decimal(str(item['precio']))
            )
            
            # Actualizar stock con sistema de ventas pendientes
            stock_anterior = producto.stock
            producto.stock -= cantidad
            
            # Si el stock es negativo, registrar como venta pendiente
            if producto.stock < 0:
                # Incrementar ventas pendientes
                producto.ventas_pendientes += abs(producto.stock)
                # Mantener stock en 0 para mostrar al cliente
                stock_actualizado = 0
            else:
                stock_actualizado = producto.stock
            
            producto.save()
            
            # Registrar movimiento de inventario
            MovimientoInventario.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_actualizado,
                motivo=f'Venta {venta.numero_venta}',
                usuario=request.user
            )
        
        return JsonResponse({
            'success': True,
            'venta_id': venta.id,
            'numero_venta': venta.numero_venta,
            'total': str(venta.total),
            'cambio': str(venta.cambio) if venta.cambio else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    for producto in productos:
        data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio_venta),
            'stock': str(producto.stock),
            'categoria': producto.categoria
        })
    
    return JsonResponse({'productos': data})


@login_required
def api_productos(request):
    categoria = request.GET.get('categoria', '')
    query = request.GET.get('q', '')
    
    productos = Producto.objects.filter(activo=True)
    
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    if query:
        productos = productos.filter(nombre__icontains=query)
    
    productos = productos.order_by('nombre')
    
    data = []
    for producto in productos:
        data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio_venta),
            'stock': str(producto.stock_real_disponible),  # Mostrar stock real disponible
            'stock_real': str(producto.stock),  # Stock real (puede ser negativo)
            'ventas_pendientes': str(producto.ventas_pendientes),  # Ventas pendientes
            'categoria': producto.categoria
        })
    
    return JsonResponse({'productos': data})


@login_required
def buscar_producto(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'})
    
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(
        activo=True,
        nombre__icontains=query
    ).order_by('nombre')[:10]
    
    data = []
    for producto in productos:
        data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio_venta),
            'stock': str(producto.stock_real_disponible),  # Usar stock_real_disponible
            'stock_real': str(producto.stock),  # Stock real (puede ser negativo)
            'ventas_pendientes': str(producto.ventas_pendientes),  # Ventas pendientes
            'categoria': producto.categoria
        })
    
    return JsonResponse({'productos': data})


@login_required
def ganancias(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    filtro = request.GET.get('filtro', 'hoy')
    hoy = timezone.now().date()
    
    if filtro == 'hoy':
        ventas = Venta.objects.filter(fecha__date=hoy, cancelada=False)
        fecha_inicio = hoy
        fecha_fin = hoy
    elif filtro == 'ayer':
        ayer = hoy - timedelta(days=1)
        ventas = Venta.objects.filter(fecha__date=ayer, cancelada=False)
        fecha_inicio = ayer
        fecha_fin = ayer
    elif filtro == 'semana':
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        ventas = Venta.objects.filter(fecha__date__gte=semana_inicio, cancelada=False)
        fecha_inicio = semana_inicio
        fecha_fin = hoy
    else:
        ventas = Venta.objects.filter(cancelada=False)
        fecha_inicio = None
        fecha_fin = None
    
    # Calcular ganancias
    ingresos = ventas.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    ganancias = Decimal('0.00')
    costos = Decimal('0.00')
    
    for venta in ventas:
        ganancias += venta.ganancia_total
        for detalle in venta.detalles.all():
            costos += detalle.producto.precio_compra * detalle.cantidad
    
    margen = (ganancias / ingresos * 100) if ingresos > 0 else Decimal('0.00')
    
    # Ganancias por producto
    ganancias_producto = []
    productos_vendidos = DetalleVenta.objects.filter(venta__in=ventas).values('producto').distinct()
    
    for producto_data in productos_vendidos:
        producto = Producto.objects.get(id=producto_data['producto'])
        detalles = DetalleVenta.objects.filter(producto=producto, venta__in=ventas)
        
        cantidad_total = sum(detalle.cantidad for detalle in detalles)
        ingresos_producto = sum(detalle.subtotal for detalle in detalles)
        costo_producto = producto.precio_compra * cantidad_total
        ganancia_producto = ingresos_producto - costo_producto
        
        ganancias_producto.append({
            'producto': producto,
            'cantidad': cantidad_total,
            'ingresos': ingresos_producto,
            'costo': costo_producto,
            'ganancia': ganancia_producto,
            'margen': (ganancia_producto / ingresos_producto * 100) if ingresos_producto > 0 else 0
        })
    
    ganancias_producto.sort(key=lambda x: x['ganancia'], reverse=True)
    
    context = {
        'filtro_actual': filtro,
        'ventas': ventas,
        'ingresos': ingresos,
        'ganancias': ganancias,
        'costos': costos,
        'margen': margen,
        'ganancias_producto': ganancias_producto,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'ganancias.html', context)


@login_required
def inventario(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        productos = productos.filter(categoria=categoria_filtro)
    
    # Movimientos recientes
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')[:20]
    
    # Calcular estadísticas reales del inventario
    from django.db.models import Sum, Count, Avg
    stats = Producto.objects.aggregate(
        total_stock=Sum('stock'),
        avg_stock=Avg('stock'),
        total_productos=Count('id'),
        productos_activos=Count('id', filter=Q(activo=True))
    )
    
    # Calcular valor total del inventario
    valor_total_inventario = sum(p.stock * p.precio_venta for p in productos)
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(stock__lt=10, activo=True).order_by('stock')
    
    # Add valor_inventario to each product
    for producto in productos:
        producto.valor_inventario = producto.stock * producto.precio_venta
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_filtro': categoria_filtro,
        'movimientos': movimientos,
        'stats': stats,
        'valor_total_inventario': valor_total_inventario,
        'productos_stock_bajo': productos_stock_bajo,
    }
    
    return render(request, 'inventario_simple.html', context)
@login_required
def gestion_categorias(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    categorias_data = []
    # Mostrar TODAS las categorías, incluyendo las que no tienen productos activos
    categorias = Producto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    for categoria in categorias:
        # Contar productos activos en esta categoría
        cantidad_activos = Producto.objects.filter(categoria=categoria, activo=True).count()
        # Contar productos totales en esta categoría
        cantidad_total = Producto.objects.filter(categoria=categoria).count()
        # Calcular inactivos
        cantidad_inactivos = cantidad_total - cantidad_activos
        
        categorias_data.append({
            'nombre': categoria,
            'cantidad': cantidad_activos,
            'cantidad_total': cantidad_total,
            'cantidad_inactivos': cantidad_inactivos
        })
    
    context = {
        'categorias': categorias_data,
    }
    
    return render(request, 'gestion_categorias_simple.html', context)


@login_required
def crear_categoria(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        
        if not nombre:
            messages.error(request, 'El nombre de la categoría es requerido')
            return redirect('gestion_categorias')
        
        # Verificar si ya existe
        if Producto.objects.filter(categoria=nombre).exists():
            messages.error(request, 'Esta categoría ya existe')
            return redirect('gestion_categorias')
        
        # Crear la categoría creando un producto temporal con stock 0 y desactivado
        # NO eliminamos el producto para que la categoría persista
        temp_producto = Producto.objects.create(
            nombre=f"_temp_{nombre}_{timezone.now().timestamp()}",
            categoria=nombre,
            precio_compra=0,
            precio_venta=0,
            stock=0,
            activo=False
        )
        
        messages.success(request, f'Categoría "{nombre}" creada exitosamente')
        return redirect('gestion_categorias')
    
    return redirect('gestion_categorias')


@login_required
def editar_categoria(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        nombre_actual = request.POST.get('nombre_actual').strip()
        nombre_nuevo = request.POST.get('nombre_nuevo').strip()
        
        if not nombre_actual or not nombre_nuevo:
            messages.error(request, 'Ambos nombres son requeridos')
            return redirect('gestion_categorias')
        
        # Actualizar todos los productos con la categoría antigua
        productos_actualizados = Producto.objects.filter(categoria=nombre_actual).update(categoria=nombre_nuevo)
        
        if productos_actualizados > 0:
            messages.success(request, f'Categoría actualizada. {productos_actualizados} productos modificados.')
        else:
            messages.warning(request, 'No se encontraron productos con esa categoría.')
        
        return redirect('gestion_categorias')
    
    return redirect('gestion_categorias')


@login_required
def eliminar_categoria(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre_eliminar').strip()
        
        if not nombre:
            messages.error(request, 'El nombre de la categoría es requerido')
            return redirect('gestion_categorias')
        
        # Verificar si hay productos con esta categoría
        productos_activos_count = Producto.objects.filter(categoria=nombre, activo=True).count()
        
        if productos_activos_count > 0:
            messages.error(request, f'No se puede eliminar la categoría porque tiene {productos_activos_count} productos activos asociados')
            return redirect('gestion_categorias')
        
        # Eliminar todos los productos inactivos de esta categoría
        productos_inactivos = Producto.objects.filter(categoria=nombre, activo=False)
        eliminados = productos_inactivos.count()
        productos_inactivos.delete()
        
        if eliminados > 0:
            messages.success(request, f'Categoría "{nombre}" eliminada. Se eliminaron {eliminados} productos inactivos.')
        else:
            messages.warning(request, f'La categoría "{nombre}" no existía o ya fue eliminada.')
        
        return redirect('gestion_categorias')
    
    return redirect('gestion_categorias')


@login_required
def editar_categoria(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        nombre_actual = request.POST.get('nombre_actual').strip()
        nombre_nuevo = request.POST.get('nombre_nuevo').strip()
        
        if not nombre_actual or not nombre_nuevo:
            messages.error(request, 'Ambos nombres son requeridos')
            return redirect('gestion_categorias')
        
        # Actualizar todos los productos con la categoría antigua
        productos_actualizados = Producto.objects.filter(categoria=nombre_actual).update(categoria=nombre_nuevo)
        
        if productos_actualizados > 0:
            messages.success(request, f'Categoría actualizada. {productos_actualizados} productos modificados.')
        else:
            messages.warning(request, 'No se encontraron productos con esa categoría.')
        
        return redirect('gestion_categorias')
    
    return redirect('gestion_categorias')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Producto, MovimientoInventario


@login_required
def toggle_estado_producto(request, producto_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    producto = get_object_or_404(Producto, id=producto_id)
    producto.activo = not producto.activo
    producto.save()
    
    estado = "activado" if producto.activo else "desactivado"
    messages.success(request, f'Producto {producto.nombre} {estado} exitosamente')
    return redirect('gestion_productos')


@login_required
def edicion_masiva_productos(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        productos_seleccionados = request.POST.get('productos_seleccionados', '').split(',')
        accion = request.POST.get('accion_masiva')
        
        if not productos_seleccionados or not accion:
            messages.error(request, 'Selecciona productos y una acción')
            return redirect('gestion_productos')
        
        productos = Producto.objects.filter(id__in=productos_seleccionados)
        count = 0
        
        if accion == 'cambiar_categoria':
            nueva_categoria = request.POST.get('nueva_categoria_masiva')
            count = productos.update(categoria=nueva_categoria)
            messages.success(request, f'{count} productos actualizados a la categoría "{nueva_categoria}"')
            
        elif accion == 'cambiar_precio_venta':
            tipo_ajuste = request.POST.get('tipo_ajuste_precio')
            valor = Decimal(request.POST.get('valor_ajuste'))
            
            for producto in productos:
                if tipo_ajuste == 'fijo':
                    producto.precio_venta = valor
                elif tipo_ajuste == 'porcentaje':
                    producto.precio_venta = producto.precio_venta * (1 + valor/100)
                elif tipo_ajuste == 'margen':
                    producto.precio_venta = producto.precio_compra / (1 - valor/100)
                producto.save()
                count += 1
            
            messages.success(request, f'Precios actualizados en {count} productos')
            
        elif accion == 'ajustar_stock':
            tipo_ajuste = request.POST.get('tipo_ajuste_stock')
            valor = Decimal(request.POST.get('valor_stock'))
            
            for producto in productos:
                if tipo_ajuste == 'fijo':
                    producto.stock = valor
                elif tipo_ajuste == 'sumar':
                    producto.stock += valor
                elif tipo_ajuste == 'restar':
                    producto.stock = max(0, producto.stock - valor)
                producto.save()
                count += 1
            
            messages.success(request, f'Stock ajustado en {count} productos')
            
        elif accion == 'activar_desactivar':
            estado = request.POST.get('estado_producto')
            activar = estado == 'activar'
            count = productos.update(activo=activar)
            messages.success(request, f'{count} productos {"activados" if activar else "desactivados"}')
            
        elif accion == 'eliminar':
            nombres = [p.nombre for p in productos]
            count = productos.delete()[0]
            messages.success(request, f'{count} productos eliminados: {", ".join(nombres)}')
        
        return redirect('gestion_productos')
    
    return redirect('gestion_productos')


@login_required
def historial_cambios(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    # Obtener movimientos de inventario recientes
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')[:50]
    
    context = {
        'movimientos': movimientos,
    }
    
    return render(request, 'historial_cambios.html', context)


@login_required
def recepcion_mercancia(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        tipo_ajuste = request.POST.get('tipoAjuste')
        cantidad = Decimal(request.POST.get('cantidad'))
        motivo = request.POST.get('motivo', 'Recepción de mercancía')
        
        if not producto_id or not tipo_ajuste or cantidad < 0:
            messages.error(request, 'Todos los campos son requeridos')
            return redirect('recepcion_mercancia')
        
        producto = get_object_or_404(Producto, id=producto_id)
        stock_anterior = producto.stock
        
        if tipo_ajuste == 'sumar':
            # Sistema automático de resta de ventas pendientes
            stock_calculado = producto.stock + cantidad
            
            # Si hay ventas pendientes, restarlas automáticamente
            if producto.ventas_pendientes > 0:
                if stock_calculado >= producto.ventas_pendientes:
                    # El nuevo stock cubre todas las ventas pendientes
                    stock_calculado -= producto.ventas_pendientes
                    producto.ventas_pendientes = 0
                    messages.info(request, f'Se cubrieron todas las ventas pendientes de "{producto.nombre}"')
                else:
                    # El nuevo stock solo cubre parte de las ventas pendientes
                    producto.ventas_pendientes -= stock_calculado
                    stock_calculado = 0
                    messages.info(request, f'Se cubrieron parcialmente las ventas pendientes de "{producto.nombre}"')
            
            producto.stock = stock_calculado
            tipo_movimiento = 'entrada'
        elif tipo_ajuste == 'fijo':
            # Para ajuste fijo, primero resetear ventas pendientes si el stock es suficiente
            if cantidad >= producto.ventas_pendientes:
                cantidad -= producto.ventas_pendientes
                producto.ventas_pendientes = 0
                messages.info(request, f'Se cubrieron todas las ventas pendientes de "{producto.nombre}"')
            else:
                # Si el stock fijo no cubre las pendientes, mantener las pendientes
                producto.ventas_pendientes -= cantidad
                cantidad = 0
                messages.info(request, f'Se cubrieron parcialmente las ventas pendientes de "{producto.nombre}"')
            
            producto.stock = cantidad
            tipo_movimiento = 'ajuste'
        else:
            messages.error(request, 'Tipo de ajuste no válido')
            return redirect('recepcion_mercancia')
        
        producto.save()
        
        # Registrar movimiento de inventario
        MovimientoInventario.objects.create(
            producto=producto,
            tipo=tipo_movimiento,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=producto.stock,
            motivo=motivo,
            usuario=request.user
        )
        
        messages.success(request, f'Stock de "{producto.nombre}" actualizado: {stock_anterior} → {producto.stock}')
        return redirect('recepcion_mercancia')
    
    # GET request - mostrar formulario
    productos = Producto.objects.filter(activo=True).order_by('categoria', 'nombre')
    
    # Resumen del día
    from django.utils import timezone
    hoy = timezone.localtime(timezone.now()).date()
    
    movimientos_hoy = MovimientoInventario.objects.filter(
        fecha__date=hoy,
        tipo__in=['entrada', 'ajuste']
    ).order_by('-fecha')
    
    resumen_dia = {
        'productos_actualizados': movimientos_hoy.values('producto').distinct().count(),
        'total_unidades': movimientos_hoy.aggregate(total=Sum('cantidad'))['total'] or 0,
        'valor_mercancia': sum(
            mov.cantidad * mov.producto.precio_compra 
            for mov in movimientos_hoy
        )
    }
    
    context = {
        'productos': productos,
        'movimientos_hoy': movimientos_hoy,
        'resumen_dia': resumen_dia,
    }
    
    return render(request, 'recepcion_mercancia.html', context)


@login_required
def obtener_producto(request, producto_id):
    if request.method == 'GET':
        producto = get_object_or_404(Producto, id=producto_id)
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'precio_compra': float(producto.precio_compra),
            'precio_venta': float(producto.precio_venta),
            'stock': float(producto.stock),
            'activo': producto.activo
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def gestion_empleados(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    empleados = User.objects.all().order_by('username')
    
    # Check if empleado exists, create if not
    try:
        User.objects.get(username='empleado')
    except User.DoesNotExist:
        empleado = User.objects.create_user(
            username='empleado',
            email='empleado@splashpos.com',
            password='emp123',
            first_name='Empleado',
            last_name='Test',
            is_staff=False,
            is_active=True
        )
        print(f"✅ Usuario 'empleado' creado con contraseña 'emp123'")
    
    # Add password display for admin (simple approach)
    password_map = {
        'admin': 'admin123',
        'gilbert': '123456',
        'empleado': 'emp123',
        'user': '123456',
    }
    
    for empleado in empleados:
        empleado.password_display = password_map.get(empleado.username, '123456')
    
    context = {
        'empleados': empleados,
    }
    
    return render(request, 'gestion_empleados.html', context)


@login_required
def crear_empleado(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # Validaciones
        if not username or not password:
            messages.error(request, 'Usuario y contraseña son requeridos')
            return redirect('gestion_empleados')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('gestion_empleados')
        
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('gestion_empleados')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return redirect('gestion_empleados')
        
        # Crear empleado
        empleado = User.objects.create_user(
            username=username,
            email=email or '',
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_staff=is_staff,
            is_active=is_active
        )
        
        messages.success(request, f'Empleado "{empleado.username}" creado exitosamente')
        return redirect('gestion_empleados')
    
    return redirect('gestion_empleados')


@login_required
def editar_empleado(request):
    if not request.user.is_staff:
        return redirect('pos')
    
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado_id')
        username = request.POST.get('username').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            empleado = User.objects.get(id=empleado_id)
            
            # Validar username único
            if User.objects.exclude(id=empleado_id).filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
                return redirect('gestion_empleados')
            
            # Validar contraseña si se proporciona
            if password and password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden')
                return redirect('gestion_empleados')
            
            if password and len(password) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
                return redirect('gestion_empleados')
            
            # Actualizar datos
            empleado.username = username
            empleado.email = email
            empleado.first_name = first_name
            empleado.last_name = last_name
            empleado.is_staff = is_staff
            empleado.is_active = is_active
            
            if password:
                empleado.set_password(password)
            
            empleado.save()
            
            messages.success(request, f'Empleado "{empleado.username}" actualizado exitosamente')
            
        except User.DoesNotExist:
            messages.error(request, 'Empleado no encontrado')
        
        return redirect('gestion_empleados')
    
    return redirect('gestion_empleados')


@login_required
def toggle_estado_empleado(request, empleado_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    try:
        empleado = User.objects.get(id=empleado_id)
        
        # No permitir desactivar al propio administrador
        if empleado.username == request.user.username:
            messages.error(request, 'No puedes cambiar tu propio estado')
            return redirect('gestion_empleados')
        
        empleado.is_active = not empleado.is_active
        empleado.save()
        
        estado = 'activado' if empleado.is_active else 'desactivado'
        messages.success(request, f'Empleado "{empleado.username}" {estado} exitosamente')
        
    except User.DoesNotExist:
        messages.error(request, 'Empleado no encontrado')
    
    return redirect('gestion_empleados')


@login_required
def eliminar_empleado(request, empleado_id):
    if not request.user.is_staff:
        return redirect('pos')
    
    try:
        empleado = User.objects.get(id=empleado_id)
        
        # No permitir eliminar administradores
        if empleado.is_staff:
            messages.error(request, 'No se puede eliminar a un administrador')
            return redirect('gestion_empleados')
        
        # No permitir eliminarse a sí mismo
        if empleado.username == request.user.username:
            messages.error(request, 'No puedes eliminarte a ti mismo')
            return redirect('gestion_empleados')
        
        username = empleado.username
        empleado.delete()
        
        messages.success(request, f'Empleado "{username}" eliminado exitosamente')
        
    except User.DoesNotExist:
        messages.error(request, 'Empleado no encontrado')
    
    return redirect('gestion_empleados')
