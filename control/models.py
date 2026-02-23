from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


# ==========================
# USUARIO
# ==========================
class Usuario(AbstractUser):
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    EMAIL_FIELD = "email"
    objects = UserManager()

    ROLE_CHOICES = [
        ("admin", "Administrador"),
        ("usuario", "Usuario/Atendedora"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="usuario", verbose_name="Rol")
    nombre = models.CharField(max_length=150, verbose_name="Nombre Completo")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre} ({self.get_role_display()})"


# ==========================
# SUCURSAL / ZONA / MAQUINA
# ==========================
class Sucursal(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    telefono = models.CharField(
        max_length=12,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{8,12}$",
                message="El teléfono debe contener solo números y tener entre 8 y 12 dígitos.",
            )
        ],
    )
    caja_inicial = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Zona(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="zonas")
    nombre = models.CharField(max_length=80)
    orden = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ["sucursal", "orden", "nombre"]

    def __str__(self):
        return f"{self.sucursal.nombre} - {self.nombre}"


class Maquina(models.Model):
    is_active = models.BooleanField(default=True)

    ESTADO_CHOICES = [
        ("Operativa", "Operativa"),
        ("Mantenimiento", "Mantenimiento"),
        ("Retirada", "Retirada"),
    ]

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="maquinas", verbose_name="Sucursal")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name="maquinas", verbose_name="Zona")
    contador_inicial_entrada = models.PositiveBigIntegerField(default=0)
    contador_inicial_salida = models.PositiveBigIntegerField(default=0)
    numero_maquina = models.IntegerField(verbose_name="Número de Máquina")
    codigo_interno = models.CharField(max_length=80, blank=True, verbose_name="Código Interno")
    nombre_juego = models.CharField(max_length=120, verbose_name="Nombre del Juego")
    servidor = models.CharField(max_length=60, blank=True, default="", verbose_name="Servidor")

    modelo = models.CharField(max_length=80, blank=True, verbose_name="Modelo")
    numero_serie = models.CharField(max_length=120, blank=True, verbose_name="Número de Serie")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Operativa", verbose_name="Estado")
    ubicacion_detalle = models.CharField(max_length=150, blank=True, verbose_name="Detalle de Ubicación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"
        ordering = ["sucursal", "zona", "numero_maquina"]
        constraints = [
            models.UniqueConstraint(fields=["zona", "numero_maquina"], name="uniq_maquina_por_zona")
        ]

    def __str__(self):
        return f"{self.sucursal.nombre} / {self.zona.nombre} / M{self.numero_maquina:02d} - {self.nombre_juego}"

    def clean(self):
        super().clean()
        if self.zona_id and self.sucursal_id:
            if self.zona.sucursal_id != self.sucursal_id:
                raise ValidationError({"sucursal": "La sucursal debe coincidir con la sucursal de la zona seleccionada."})


# ==========================
# TURNO / LECTURAS
# ==========================
class Turno(models.Model):
    TIPO_TURNO_CHOICES = [("Mañana", "Mañana"), ("Tarde", "Tarde"), ("Noche", "Noche")]
    ESTADO_CHOICES = [("Abierto", "Abierto"), ("Cerrado", "Cerrado")]

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="turnos", verbose_name="Sucursal")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="turnos", verbose_name="Usuario")

    fecha = models.DateField(verbose_name="Fecha")
    tipo_turno = models.CharField(max_length=20, choices=TIPO_TURNO_CHOICES, verbose_name="Tipo de Turno")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Abierto", verbose_name="Estado")

    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    total_cierre = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Total de Cierre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.sucursal.nombre} - {self.fecha} ({self.tipo_turno})"

    def clean(self):
        if not self.usuario_id:
            return
        if self.estado == "Abierto":
            existe = Turno.objects.filter(usuario_id=self.usuario_id, estado="Abierto").exclude(pk=self.pk).exists()
            if existe:
                raise ValidationError("Ya tiene un turno abierto. Debe cerrarlo antes de abrir uno nuevo.")

class LecturaMaquina(models.Model):
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="lecturas", verbose_name="Turno")
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name="lecturas", verbose_name="Máquina")

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="lecturas", verbose_name="Sucursal")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name="lecturas", verbose_name="Zona")

    numero_maquina = models.IntegerField(verbose_name="Número de Máquina")
    nombre_juego = models.CharField(max_length=120, verbose_name="Nombre del Juego")

    entrada = models.BigIntegerField(verbose_name="Entrada")
    salida = models.BigIntegerField(verbose_name="Salida")
    total  = models.BigIntegerField(verbose_name="Total")

    nota = models.CharField(max_length=255, blank=True, verbose_name="Nota")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lecturas", verbose_name="Usuario")

    fecha_trabajo = models.DateField(null=True, blank=True, db_index=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    entrada_anterior = models.PositiveBigIntegerField(default=0)
    salida_anterior = models.PositiveBigIntegerField(default=0)
    entrada_dia = models.BigIntegerField(default=0)
    salida_dia = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = "Lectura de Máquina"
        verbose_name_plural = "Lecturas de Máquinas"
        ordering = ["-fecha_registro"]
        constraints = [
            models.UniqueConstraint(fields=["turno", "maquina"], name="uniq_lectura_maquina_por_turno")
        ]

    def __str__(self):
        return f"Lectura {self.numero_maquina} - {self.nombre_juego} ({self.fecha_registro})"

    def save(self, *args, **kwargs):
    # 1) fecha_trabajo SIEMPRE desde el turno (si existe)
        if self.turno_id and not self.fecha_trabajo:
            self.fecha_trabajo = self.turno.fecha

        # 2) copiar datos fijos desde la máquina
        if self.maquina_id:
            self.numero_maquina = self.maquina.numero_maquina
            self.nombre_juego = self.maquina.nombre_juego
            self.sucursal = self.maquina.sucursal
            self.zona = self.maquina.zona

        # 3) SOLO al crear: calcular anterior/parciales/total
        if not self.pk:
            # import local para evitar circular import
            from .utils import get_referencia_anterior

            entrada_ant, salida_ant, fuente = get_referencia_anterior(
                self.maquina,
                self.fecha_trabajo
            )

            self.entrada_anterior = int(entrada_ant or 0)
            self.salida_anterior = int(salida_ant or 0)

            self.entrada_dia = int(self.entrada or 0) - self.entrada_anterior
            self.salida_dia  = int(self.salida or 0)  - self.salida_anterior
            self.total       = self.entrada_dia - self.salida_dia

        super().save(*args, **kwargs)



# ==========================
# CUADRATURA DIARIA (EXCEL GRANDE)
# ==========================
class CuadraturaCajaDiaria(models.Model):
    fecha = models.DateField(default=timezone.now, verbose_name="Fecha")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="cuadraturas_diarias", verbose_name="Sucursal")
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True, related_name="cuadraturas_diarias", verbose_name="Turno")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cuadraturas_diarias", verbose_name="Usuario")


    numeral_dia = models.BigIntegerField(default=0)
    numeral_acumulado = models.BigIntegerField(default=0, verbose_name="Numeral Acumulado")  # ✅ recomendado

    sorteos_ant = models.IntegerField(default=0); sorteos_dia = models.IntegerField(default=0); sorteos_acum = models.IntegerField(default=0); sorteos_notas = models.TextField(blank=True, default="")
    gastos_ant = models.IntegerField(default=0); gastos_dia = models.IntegerField(default=0); gastos_acum = models.IntegerField(default=0); gastos_notas = models.TextField(blank=True, default="")
    sueldo_b_ant = models.IntegerField(default=0); sueldo_b_dia = models.IntegerField(default=0); sueldo_b_acum = models.IntegerField(default=0); sueldo_b_notas = models.TextField(blank=True, default="")
    redbank_ant = models.IntegerField(default=0); redbank_dia = models.IntegerField(default=0); redbank_acum = models.IntegerField(default=0); redbank_notas = models.TextField(blank=True, default="")
    regalos_ant = models.IntegerField(default=0); regalos_dia = models.IntegerField(default=0); regalos_acum = models.IntegerField(default=0); regalos_notas = models.TextField(blank=True, default="")
    taxi_ant = models.IntegerField(default=0); taxi_dia = models.IntegerField(default=0); taxi_acum = models.IntegerField(default=0); taxi_notas = models.TextField(blank=True, default="")
    jugados_ant = models.IntegerField(default=0); jugados_dia = models.IntegerField(default=0); jugados_acum = models.IntegerField(default=0); jugados_notas = models.TextField(blank=True, default="")
    transfer_ant = models.IntegerField(default=0); transfer_dia = models.IntegerField(default=0); transfer_acum = models.IntegerField(default=0); transfer_notas = models.TextField(blank=True, default="")
    otros_1_ant = models.IntegerField(default=0); otros_1_dia = models.IntegerField(default=0); otros_1_acum = models.IntegerField(default=0); otros_1_notas = models.TextField(blank=True, default="")
    otros_2_ant = models.IntegerField(default=0); otros_2_dia = models.IntegerField(default=0); otros_2_acum = models.IntegerField(default=0); otros_2_notas = models.TextField(blank=True, default="")
    otros_3_ant = models.IntegerField(default=0); otros_3_dia = models.IntegerField(default=0); otros_3_acum = models.IntegerField(default=0); otros_3_notas = models.TextField(blank=True, default="")
    descuadre_ant = models.IntegerField(default=0); descuadre_dia = models.IntegerField(default=0); descuadre_acum = models.IntegerField(default=0); descuadre_notas = models.TextField(blank=True, default="")

    prestamos = models.IntegerField(null=True, blank=True, default=0)
    prestamos_notas = models.TextField(blank=True, default="")

    caja = models.IntegerField(default=0, verbose_name="Caja")
    retiro_diario = models.IntegerField(default=0, verbose_name="Retiro Diario")
    ganancia = models.IntegerField(default=0, verbose_name="Ganancia")
    total_efectivo = models.IntegerField(default=0, verbose_name="Total Efectivo")
    observaciones = models.TextField(blank=True, default="", verbose_name="Observaciones")

    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    ef_20000 = models.IntegerField(null=True, blank=True, default=0)
    ef_10000 = models.IntegerField(null=True, blank=True, default=0)
    ef_5000  = models.IntegerField(null=True, blank=True, default=0)
    ef_2000  = models.IntegerField(null=True, blank=True, default=0)
    ef_1000  = models.IntegerField(null=True, blank=True, default=0)
    ef_monedas = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        ordering = ["-fecha", "-creado_el"]
        constraints = [
            models.UniqueConstraint(
                fields=["sucursal", "fecha"],
                name="uniq_cuadratura_por_sucursal_fecha"
            )
        ]
    def __str__(self):
        return f"Cuadratura diaria {self.sucursal.nombre} - {self.fecha}"

    def total_gastos_dia(self) -> int:
        return (
            (self.sorteos_dia or 0)
            + (self.gastos_dia or 0)
            + (self.sueldo_b_dia or 0)
            + (self.redbank_dia or 0)
            + (self.regalos_dia or 0)
            + (self.taxi_dia or 0)
            + (self.jugados_dia or 0)  # ✅ faltaba
            + (self.transfer_dia or 0)
            + (self.otros_1_dia or 0)
            + (self.otros_2_dia or 0)
            + (self.otros_3_dia or 0)
            + (self.descuadre_dia or 0)
        )

    @property
    def desglose_efectivo_total(self):
        return (
            (self.ef_20000 or 0)
            + (self.ef_10000 or 0)
            + (self.ef_5000 or 0)
            + (self.ef_2000 or 0)
            + (self.ef_1000 or 0)
            + (self.ef_monedas or 0)
        )
# ==========================
# DETALLES CUADRATURA (ITEMS)
# ==========================

class CuadraturaDetalle(models.Model):
    class Tipo(models.TextChoices):
        GASTOS = "GASTOS", "Gastos"
        SUELDOS = "SUELDOS", "Sueldos"
        REGALOS = "REGALOS", "Regalos"
        TAXI = "TAXI", "Taxi"
        JUGADOS = "JUGADOS", "Jugados"
        OTROS = "OTROS", "Otros"

    cuadratura = models.ForeignKey(
        CuadraturaCajaDiaria,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name="Cuadratura"
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, verbose_name="Tipo")

    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    monto = models.IntegerField(default=0, verbose_name="Monto")
    detalle = models.TextField(blank=True, default="", verbose_name="Detalle")  # ✅ mejor

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["tipo", "creado_en"]

    def __str__(self):
        return f"{self.tipo} - {self.nombre} (${self.monto})"


# ==========================
# ENCUADRE ADMIN
# ==========================
class EncuadreCajaAdmin(models.Model):
    fecha = models.DateField(default=timezone.now, verbose_name="Fecha")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="encuadres_admin")
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True, related_name="encuadres_admin")

    usuario_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="encuadres_admin")
    nombre_responsable = models.CharField(max_length=200, blank=True, verbose_name="Nombre Responsable")

    total_zona = models.IntegerField(default=0, verbose_name="Total Zona")

    caja_numeral = models.IntegerField(default=0, verbose_name="Caja Numeral")
    prestamos = models.IntegerField(default=0, verbose_name="Préstamos")
    redbank_retiros = models.IntegerField(default=0, verbose_name="Redbank Retiros")
    total_caja = models.IntegerField(default=0, verbose_name="Total Caja")

    billete_20000 = models.IntegerField(default=0, verbose_name="Billetes 20,000")
    billete_10000 = models.IntegerField(default=0, verbose_name="Billetes 10,000")
    billete_5000 = models.IntegerField(default=0, verbose_name="Billetes 5,000")
    billete_2000 = models.IntegerField(default=0, verbose_name="Billetes 2,000")
    billete_1000 = models.IntegerField(default=0, verbose_name="Billetes 1,000")
    monedas_total = models.IntegerField(default=0, verbose_name="Monedas Total")

    descuadre = models.IntegerField(default=0, verbose_name="Descuadre")
    observaciones = models.TextField(blank=True, default="", verbose_name="Observaciones")

    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-creado_el"]

    def __str__(self):
        return f"Encuadre admin {self.sucursal.nombre} - {self.fecha}"


# ==========================
# CIERRE DE TURNO (FORMSETS)
# ==========================
class CierreTurno(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, related_name="cierre")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="cierres")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="cierres")
    fecha = models.DateField(default=timezone.now)
    caja_base = models.BigIntegerField(default=0)
    retiro_diario = models.BigIntegerField(default=0)
    prestamos_salida = models.IntegerField(default=0)
    total_numeral = models.BigIntegerField(default=0)
    total_gastos = models.BigIntegerField(default=0)
    total_esperado = models.BigIntegerField(default=0)
    total_efectivo_contado = models.BigIntegerField(default=0)
    descuadre = models.BigIntegerField(default=0)
    observaciones = models.TextField(blank=True, default="")
    redbank_retiros = models.BigIntegerField(default=0)
    total_lecturas_turno = models.BigIntegerField(default=0)


class CierreTurnoMovimiento(models.Model):
    TIPO_CHOICES = [
        ("SORTEOS", "Sorteos"),
        ("GASTOS", "Gastos"),
        ("SUELDO_B", "Sueldo B"),
        ("REDBANK", "Redbank"),
        ("REGALOS", "Regalos"),
        ("TAXI", "Taxi"),
        ("JUGADOS", "Jugados"),
        ("TRANSFER", "Transfer"),
        ("OTROS_1", "Otros 1"),
        ("OTROS_2", "Otros 2"),
        ("OTROS_3", "Otros 3"),
        ("DESCUADRE", "Descuadre"),
    ]
    cierre = models.ForeignKey(CierreTurno, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.IntegerField(default=0)
    descripcion = models.CharField(max_length=255, blank=True, default="")
    nota = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["tipo"]


class CierreTurnoPago(models.Model):
    TIPO_CHOICES = [
        ("EFECTIVO", "Efectivo"),
        ("REDBANK", "Redbank"),
        ("TRANSFER", "Transferencia"),
        ("OTRO", "Otro"),
    ]
    cierre = models.ForeignKey(CierreTurno, on_delete=models.CASCADE, related_name="pagos")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.IntegerField(default=0)
    referencia = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ["tipo"]


class CierreTurnoDenominacion(models.Model):
    TIPO_CHOICES = [("BILLETE", "Billete"), ("MONEDA", "Moneda")]
    cierre = models.ForeignKey(CierreTurno, on_delete=models.CASCADE, related_name="denominaciones")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    denominacion = models.IntegerField()  # 20000, 10000, 5000...
    cantidad = models.IntegerField(default=0)

    class Meta:
        unique_together = ("cierre", "tipo", "denominacion")
        ordering = ["-tipo", "-denominacion"]
        

class CierreTurnoZona(models.Model):
    cierre = models.ForeignKey("CierreTurno", related_name="zonas", on_delete=models.CASCADE)
    zona = models.ForeignKey("Zona", on_delete=models.PROTECT)

    numeral = models.IntegerField(default=0)

    caja = models.IntegerField(default=0)
    prestamos = models.IntegerField(default=0)
    redbank = models.IntegerField(default=0)
    retiros = models.IntegerField(default=0)

    # ✅ DETALLE ENTREGADO (MONTO por denominación) - POR ZONA
    billete_20000_monto = models.IntegerField(default=0)
    billete_10000_monto = models.IntegerField(default=0)
    billete_5000_monto  = models.IntegerField(default=0)
    billete_2000_monto  = models.IntegerField(default=0)
    billete_1000_monto  = models.IntegerField(default=0)

    # ✅ MONEDAS (1 solo campo) - POR ZONA
    monedas_monto = models.IntegerField(default=0)
    detalle_entregado_total = models.IntegerField(default=0)

    descuadre = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.cierre_id} - {self.zona.nombre}"

class CicloRecaudacion(models.Model):
    sucursal = models.OneToOneField(
        "Sucursal",
        on_delete=models.CASCADE,
        related_name="ciclo_recaudacion"
    )
    inicio_ciclo = models.DateField()  # Fecha del "día 0"
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ciclo {self.sucursal} desde {self.inicio_ciclo}"
    


class ControlLecturas(models.Model):
    sucursal = models.ForeignKey("Sucursal", on_delete=models.CASCADE, related_name="controles")
    fecha_trabajo = models.DateField(db_index=True)
    turno = models.ForeignKey("Turno", on_delete=models.SET_NULL, null=True, blank=True, related_name="controles")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_general = models.BigIntegerField(default=0)

    class Meta:
        ordering = ["-fecha_trabajo", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["sucursal", "fecha_trabajo"], name="uniq_control_por_sucursal_fecha")
        ]

    def __str__(self):
        return f"Control {self.sucursal} - {self.fecha_trabajo}"


class ControlLecturasLinea(models.Model):
    control = models.ForeignKey(ControlLecturas, on_delete=models.CASCADE, related_name="lineas")

    zona = models.ForeignKey("Zona", on_delete=models.SET_NULL, null=True, blank=True)
    maquina = models.ForeignKey("Maquina", on_delete=models.SET_NULL, null=True, blank=True)

    numero_maquina = models.IntegerField()
    servidor = models.CharField(max_length=80, blank=True)
    juego = models.CharField(max_length=120, blank=True)

    entrada_historica = models.BigIntegerField(default=0)
    salida_historica = models.BigIntegerField(default=0)
    entrada_parcial = models.BigIntegerField(default=0)
    salida_parcial = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)

    class Meta:
        ordering = ["numero_maquina", "id"]