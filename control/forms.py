from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Sucursal, Zona, Maquina, Turno, LecturaMaquina, Usuario


class TurnoForm(forms.ModelForm):
    """
    Formulario para crear turnos
    """
    class Meta:
        model = Turno
        fields = ['sucursal', 'fecha', 'tipo_turno']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'sucursal': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'tipo_turno': forms.Select(attrs={'class': 'form-control form-control-lg'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha por defecto a hoy
        if not self.instance.pk:
            self.fields['fecha'].initial = timezone.now().date()
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha:
            hoy = timezone.now().date()
            fecha_minima = hoy - timedelta(days=2)
            fecha_maxima = hoy + timedelta(days=1)
            
            if fecha < fecha_minima:
                raise ValidationError('La fecha del turno no puede ser anterior a hace 2 días.')
            
            if fecha > fecha_maxima:
                raise ValidationError('La fecha del turno no puede ser posterior a mañana.')
        
        return fecha


class LecturaMaquinaForm(forms.ModelForm):
    """
    Formulario para registrar lecturas de máquinas
    """
    zona = forms.ModelChoiceField(
        queryset=Zona.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'}),
        label='Zona'
    )
    
    class Meta:
        model = LecturaMaquina
        fields = ['zona', 'maquina', 'entrada', 'salida', 'total', 'nota']
        widgets = {
            'maquina': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'entrada': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': '0'}),
            'salida': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': '0'}),
            'total': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'readonly': 'readonly'}),
            'nota': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Opcional'}),
        }
    
    def __init__(self, *args, **kwargs):
        turno = kwargs.pop('turno', None)
        super().__init__(*args, **kwargs)
        
        if turno:
            self.fields['zona'].queryset = Zona.objects.filter(
                sucursal=turno.sucursal
            ).order_by('orden', 'nombre')
            
            # Filtrar máquinas - inicialmente vacío, se llena con JS según zona seleccionada
            self.fields['maquina'].queryset = Maquina.objects.filter(
                zona__sucursal=turno.sucursal,
                estado='Operativa'
            )
        else:
            self.fields['zona'].queryset = Zona.objects.none()
            self.fields['maquina'].queryset = Maquina.objects.none()


class SucursalForm(forms.ModelForm):
    """
    Formulario para Sucursales
    """
    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ZonaForm(forms.ModelForm):
    """
    Formulario para Zonas
    """
    class Meta:
        model = Zona
        fields = ['sucursal', 'nombre', 'orden']
        widgets = {
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class MaquinaForm(forms.ModelForm):
    """
    Formulario para Máquinas
    """
    class Meta:
        model = Maquina
        fields = [
            'sucursal', 'zona', 'numero_maquina', 'codigo_interno',
            'nombre_juego', 'modelo', 'numero_serie', 'estado', 'ubicacion_detalle'
        ]
        widgets = {
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'zona': forms.Select(attrs={'class': 'form-control'}),
            'numero_maquina': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_juego': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion_detalle': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UsuarioForm(forms.ModelForm):
    """
    Formulario para crear usuarios
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'email', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data


class UsuarioEditForm(forms.ModelForm):
    """
    Formulario para editar usuarios
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Nueva Contraseña (dejar en blanco para no cambiar)',
        required=False
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Nueva Contraseña',
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'email', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
