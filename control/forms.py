from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import (
    Sucursal, Zona, Maquina, Turno, LecturaMaquina, Usuario,
    CuadraturaCajaDiaria, EncuadreCajaAdmin,
    CierreTurno, CierreTurnoZona, CierreTurnoMovimiento, CierreTurnoPago, CierreTurnoDenominacion,
)


# ======================================================
# ADMIN: ENCUADRE ESTO HAY QUE IGNORARLO
# ======================================================

class EncuadreCajaAdminForm(forms.ModelForm):
    class Meta:
        model = EncuadreCajaAdmin
        exclude = ("usuario_admin", "creado_el", "actualizado_el")
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "nombre_responsable": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# ======================================================
# CUADRATURA DIARIA (EXCEL GRANDE)
# ======================================================

class CuadraturaCajaDiariaForm(forms.ModelForm):
    class Meta:
        model = CuadraturaCajaDiaria
        fields = [
            "fecha", "sucursal",
            "sorteos_ant", "sorteos_dia", "sorteos_notas",
            "gastos_ant", "gastos_dia", "gastos_notas",
            "sueldo_b_ant", "sueldo_b_dia", "sueldo_b_notas",
            "redbank_ant", "redbank_dia", "redbank_notas",
            "regalos_ant", "regalos_dia", "regalos_notas",
            "taxi_ant", "taxi_dia", "taxi_notas",
            "jugados_ant", "jugados_dia", "jugados_notas",
            "transfer_ant", "transfer_dia", "transfer_notas",
            "otros_1_ant", "otros_1_dia", "otros_1_notas",
            "otros_2_ant", "otros_2_dia", "otros_2_notas",
            "otros_3_ant", "otros_3_dia", "otros_3_notas",
            "descuadre_ant", "descuadre_dia", "descuadre_notas",
            "caja", "retiro_diario", "observaciones",
            "ef_20000","ef_10000","ef_5000","ef_2000","ef_1000","ef_monedas",
            "prestamos", "prestamos_notas",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sucursal": forms.Select(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si tienes campo sucursal dentro del ModelForm (a veces no está en fields)
        if "sucursal" in self.fields:
            self.fields["sucursal"].queryset = Sucursal.objects.filter(is_active=True).order_by("nombre")
            self.fields["sucursal"].required = True
            self.fields["sucursal"].widget.attrs.update({
                "class": "form-select",
            })
        # Bloquear numerales (si existen en el form)
        for f in ["numeral_dia", "numeral_acumulado", "numeral_total"]:
            if f in self.fields:
                self.fields[f].disabled = True

        # Estilo + quitar flechas + permitir vacío
        for name, field in self.fields.items():
    # NO tocar estos (si los tocas, rompes el select o el date)
            if name in ["fecha", "observaciones", "sucursal"]:
                continue

            # Si algún día agregas más selects/choices, tampoco los toques aquí
            if isinstance(field, forms.ModelChoiceField) or isinstance(field, forms.ChoiceField):
                continue

            # Notas -> compact textarea
            if "notas" in name:
                field.widget = forms.Textarea(attrs={
                    "class": "form-control form-control-sm",
                    "rows": 1,
                    "placeholder": "Notas...",
                })
                continue

            # Numéricos -> SIN flechas, SIN 0 por defecto, permite vacío
            field.required = False
            field.widget = forms.TextInput(attrs={
                "class": "form-control form-control-sm text-end",
                "type": "text",                 # NO number => sin flechas
                "inputmode": "numeric",
                "autocomplete": "off",
                "placeholder": "",
            })


        # Prestamos: permite negativo (igual sin flechas)
        if "prestamos" in self.fields:
            self.fields["prestamos"].required = False
            self.fields["prestamos"].widget = forms.TextInput(attrs={
                "class": "form-control form-control-sm text-end",
                "type": "text",
                "inputmode": "numeric",
                "autocomplete": "off",
                "placeholder": "Positivo suma / Negativo resta",
            })
# ======================================================
# TURNO
# ======================================================

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["sucursal", "fecha", "tipo_turno"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control form-control-lg"}),
            "sucursal": forms.Select(attrs={"class": "form-control form-control-lg"}),
            "tipo_turno": forms.Select(attrs={"class": "form-control form-control-lg"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sucursal"].queryset = Sucursal.objects.filter(is_active=True).order_by("nombre")
  

 


# ======================================================
# LECTURA MAQUINA
# ======================================================

class LecturaMaquinaForm(forms.ModelForm):
    zona = forms.ModelChoiceField(
        queryset=Zona.objects.none(),
        widget=forms.Select(attrs={"class": "form-control form-control-lg"}),
        label="Zona",
    )

    class Meta:
        model = LecturaMaquina
        fields = ["zona", "maquina", "entrada", "salida", "total", "nota"]
        widgets = {
            "maquina": forms.Select(attrs={"class": "form-control form-control-lg"}),
            "entrada": forms.NumberInput(attrs={"class": "form-control form-control-lg", "min": "0"}),
            "salida": forms.NumberInput(attrs={"class": "form-control form-control-lg", "min": "0"}),
            "total": forms.NumberInput(attrs={"class": "form-control form-control-lg", "readonly": "readonly"}),
            "nota": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Opcional"}),
        }

    def __init__(self, *args, **kwargs):
        turno = kwargs.pop("turno", None)
        super().__init__(*args, **kwargs)

        if turno:
            self.fields["zona"].queryset = Zona.objects.filter(
                sucursal=turno.sucursal,
                is_active=True,
                sucursal__is_active=True,
            ).order_by("orden", "nombre")

            self.fields["maquina"].queryset = Maquina.objects.filter(
                sucursal=turno.sucursal,
                zona__is_active=True,
                sucursal__is_active=True,
                estado="Operativa",
            ).order_by("numero_maquina")
        else:
            self.fields["zona"].queryset = Zona.objects.filter(is_active=True)
            self.fields["maquina"].queryset = Maquina.objects.filter(estado="Operativa")

    def clean(self):
        cleaned = super().clean()
        entrada = cleaned.get("entrada")
        salida = cleaned.get("salida")
        zona = cleaned.get("zona")
        maquina = cleaned.get("maquina")
        if entrada is not None and salida is not None:
            cleaned["total"] = int(entrada) - int(salida)
        if entrada is not None and entrada < 0:
            self.add_error("entrada", "La entrada no puede ser negativa.")
        if salida is not None and salida < 0:
            self.add_error("salida", "La salida no puede ser negativa.")

        if maquina and zona and maquina.zona_id != zona.id:
            self.add_error("maquina", "La máquina seleccionada no pertenece a la zona indicada.")
        return cleaned


# ======================================================
# CRUD FORMS
# ======================================================

class SucursalForm(forms.ModelForm):
    class Meta:
        model = Sucursal
        fields = ["nombre", "direccion", "telefono", "caja_inicial", "is_active"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),

            # caja inicial: sin 0 por defecto visual, sin flechas
            "caja_inicial": forms.TextInput(attrs={
                "class": "form-control text-end",
                "inputmode": "numeric",
                "placeholder": "Ej: 200000",
            }),

            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = ["sucursal", "nombre", "orden"]
        widgets = {
            "sucursal": forms.Select(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "orden": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

      
        self.fields["sucursal"].queryset = (
            Sucursal.objects
            .filter(is_active=True)
            .order_by("nombre")
        )
class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = [
            "sucursal", "zona", "numero_maquina", "codigo_interno",
            "nombre_juego", "modelo", "numero_serie", "ubicacion_detalle","contador_inicial_entrada","contador_inicial_salida","servidor"
        ]
        widgets = {
            "servidor": forms.TextInput(attrs={"class": "form-control"}),
            "contador_inicial_entrada": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "contador_inicial_salida": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "sucursal": forms.Select(attrs={"class": "form-control"}),
            "zona": forms.Select(attrs={"class": "form-control"}),
            "numero_maquina": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "codigo_interno": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_juego": forms.TextInput(attrs={"class": "form-control"}),
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "numero_serie": forms.TextInput(attrs={"class": "form-control"}),
            "ubicacion_detalle": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["sucursal"].queryset = Sucursal.objects.filter(is_active=True)
        self.fields["zona"].queryset = Zona.objects.filter(is_active=True, sucursal__is_active=True).order_by("orden", "nombre")

        if "sucursal" in self.data:
            try:
                sucursal_id = int(self.data.get("sucursal"))
                self.fields["zona"].queryset = Zona.objects.filter(
                    sucursal_id=sucursal_id,
                    is_active=True,
                    sucursal__is_active=True
                ).order_by("orden", "nombre")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.sucursal_id:
            self.fields["zona"].queryset = Zona.objects.filter(
                sucursal_id=self.instance.sucursal_id,
                is_active=True,
                sucursal__is_active=True
            ).order_by("orden", "nombre")

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk:
            self.instance.estado = "Operativa"
        return cleaned


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ["username", "nombre", "email", "role", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned


class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Nueva Contraseña (dejar en blanco para no cambiar)",
        required=False,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmar Nueva Contraseña",
        required=False,
    )

    class Meta:
        model = Usuario
        fields = ["username", "nombre", "email", "role", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password_confirm")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned


# ======================================================
# CIERRE TURNO (COLUMNA ROJA) -> FORM + FORMSETS
# ======================================================

class CierreTurnoForm(forms.ModelForm):
    class Meta:
        model = CierreTurno
        fields = ["caja_base", "retiro_diario", "observaciones","prestamos_salida","redbank_retiros"]
        widgets = {
            "caja_base": forms.NumberInput(attrs={"class": "form-control form-control-lg", "min": "0"}),
            "prestamos_salida": forms.NumberInput(attrs={"class": "form-control form-control-lg", "min": "0"}),
            "retiro_diario": forms.NumberInput(attrs={"class": "form-control form-control-lg", "min": "0"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


from django.forms import inlineformset_factory
from .models import CierreTurno, CierreTurnoZona, Zona


CierreTurnoMovimientoFormSet = inlineformset_factory(
    parent_model=CierreTurno,
    model=CierreTurnoMovimiento,
    fields=["tipo", "monto", "descripcion", "nota"],
    extra=0,
    can_delete=False,
    widgets={
        "tipo": forms.Select(attrs={"class": "form-select form-select-sm"}),
        "monto": forms.NumberInput(attrs={"class": "form-control form-control-sm text-end", "min": "0"}),
        "descripcion": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
        "nota": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    },
)

CierreTurnoPagoFormSet = inlineformset_factory(
    parent_model=CierreTurno,
    model=CierreTurnoPago,
    fields=["tipo", "monto", "referencia"],
    extra=0,
    can_delete=False,
    widgets={
        "tipo": forms.Select(attrs={"class": "form-select form-select-sm"}),
        "monto": forms.NumberInput(attrs={"class": "form-control form-control-sm text-end", "min": "0"}),
        "referencia": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    },
)

CierreTurnoDenFormSet = inlineformset_factory(
    parent_model=CierreTurno,
    model=CierreTurnoDenominacion,
    fields=["tipo", "denominacion", "cantidad"],
    extra=0,
    can_delete=False,
    widgets={
        "tipo": forms.HiddenInput(),  # o Select si lo quieres ver
        "denominacion": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "readonly":"readonly"}),
        "cantidad": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
    },
)


class CierreTurnoZonaForm(forms.ModelForm):
    class Meta:
        model = CierreTurnoZona
        fields = [
            "zona",
            "numeral",
            "caja",
            "prestamos",
            "redbank",
            "retiros",
            "detalle_entregado_total",
            "billete_20000_monto",
            "billete_10000_monto",
            "billete_5000_monto",
            "billete_2000_monto",
            "billete_1000_monto",
            "monedas_monto",
        ]
        widgets = {
            "zona": forms.HiddenInput(),
            "numeral": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "readonly": "readonly"}),
            "caja": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min": "0"}),
            "prestamos": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min": "0"}),
            "redbank": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min": "0"}),
            "retiros": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min": "0"}),
            "detalle_entregado_total": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min": "0"}),
            "billete_20000_monto": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
            "billete_10000_monto": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
            "billete_5000_monto":  forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
            "billete_2000_monto":  forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
            "billete_1000_monto":  forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),

            "monedas_monto": forms.NumberInput(attrs={"class":"form-control form-control-sm text-end", "min":"0"}),
        }

CierreTurnoZonaFormSet = inlineformset_factory(
    parent_model=CierreTurno,
    model=CierreTurnoZona,
    form=CierreTurnoZonaForm,
    extra=0,
    can_delete=False,
)



