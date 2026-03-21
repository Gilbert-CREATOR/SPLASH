from django import template

register = template.Library()

@register.filter
def pluck(list_of_dicts, key):
    return [d.get(key) for d in list_of_dicts]

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Suma el valor al argumento"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_number(value):
    """Formatea números con separador de miles (12,000)"""
    try:
        if value is None:
            return "0"
        
        # Convertir a número
        if isinstance(value, str):
            value = float(value)
        
        # Formatear sin decimales si es entero
        if value == int(value):
            return "{:,}".format(int(value))
        else:
            return "{:,.2f}".format(value).rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return "0"

@register.filter
def format_currency(value):
    """Formatea moneda con símbolo $ y separador de miles ($12,000)"""
    try:
        if value is None:
            return "$0"
        
        # Convertir a número
        if isinstance(value, str):
            value = float(value)
        
        # Formatear sin decimales si es entero
        if value == int(value):
            return "${:,}".format(int(value))
        else:
            return "${:,.2f}".format(value).rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return "$0"