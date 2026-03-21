from django import forms
from .models import Cita, Marca, Modelo, perfil, Servicio, Categoria, Producto, OrdenCafeteria, DetalleOrden, Factura
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import time


HORAS_BASE = [
    '07:00','07:30','08:00','08:30','09:00','09:30',
    '10:00','10:30','11:00','11:30','12:00','12:30',
    '13:00','13:30','14:00','14:30',
    '15:00','15:30','16:00','16:30',
    '17:00','17:30','18:00','18:30',
    '19:00','19:30','20:00'
]


class CitaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        fecha = kwargs.pop('fecha', None)
        super().__init__(*args, **kwargs)

        horas_disponibles = HORAS_BASE

        if fecha:

            horas_ocupadas = Cita.objects.filter(
                fecha=fecha
            ).values_list('hora', flat=True)

            # Convertir posibles objetos time a string
            horas_ocupadas = [
                h.strftime("%H:%M") if hasattr(h, "strftime") else str(h)
                for h in horas_ocupadas
            ]

            horas_disponibles = [
                h for h in HORAS_BASE if h not in horas_ocupadas
            ]

        self.fields['hora'] = forms.ChoiceField(
            choices=[(h, h) for h in horas_disponibles]
        )

        self.fields['modelo'].queryset = Modelo.objects.none()

        if 'marca' in self.data:
            try:
                marca_id = int(self.data.get('marca'))
                self.fields['modelo'].queryset = Modelo.objects.filter(
                    marca_id=marca_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.marca:
            self.fields['modelo'].queryset = Modelo.objects.filter(
                marca=self.instance.marca
            )

    class Meta:
        model = Cita
        fields = [
            'nombre',
            'telefono',
            'email',
            'marca',
            'modelo',
            'servicio',
            'fecha',
            'hora'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }

    # Validación extra para evitar doble reserva
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:

            existe = Cita.objects.filter(
                fecha=fecha,
                hora=str(hora)
            ).exists()

            if existe:
                raise forms.ValidationError(
                    "Esta hora ya fue reservada. Por favor selecciona otra."
                )

        return cleaned_data


class PerfilForm(forms.ModelForm):
    class Meta:
        model = perfil
        fields = ['foto_perfil']


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio']


class EmpleadoForm(forms.ModelForm):
    rol = forms.ChoiceField(
        choices=perfil.ROL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccionar rol'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Toyota'
            })
        }


class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['marca', 'nombre']
        widgets = {
            'marca': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Corolla'
            })
        }


# ==========================
# FORMULARIOS DE CAFETERÍA
# ==========================

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bebidas'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'imagen', 
                 'activo', 'popular', 'preparacion_tiempo', 'stock', 'ingredientes']
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Café Americano'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'popular': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'preparacion_tiempo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'ingredientes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ingredientes o alérgenos'
            })
        }


class DetalleOrdenForm(forms.ModelForm):
    class Meta:
        model = DetalleOrden
        fields = ['producto', 'cantidad', 'notas']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control producto-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'min': 1,
                'max': 99,
                'value': 1
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas especiales (opcional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos y con stock
        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True, 
            stock__gt=0
        ).order_by('categoria__orden', 'categoria__nombre', 'nombre')


class OrdenCafeteriaForm(forms.ModelForm):
    class Meta:
        model = OrdenCafeteria
        fields = ['cliente_nombre', 'cliente_telefono', 'notas']
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'cliente_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            })
        }


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['metodo_pago', 'notas']
        widgets = {
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas de la factura'
            })
        }


# Formset para detalles de orden
DetalleOrdenFormSet = forms.inlineformset_factory(
    OrdenCafeteria,
    DetalleOrden,
    form=DetalleOrdenForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)