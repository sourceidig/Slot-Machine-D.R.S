from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con rol
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('usuario', 'Usuario/Atendedora'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='usuario',
        verbose_name='Rol'
    )
    nombre = models.CharField(max_length=150, verbose_name='Nombre Completo')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_role_display()})"


class Sucursal(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    telefono = models.CharField(
    max_length=12,
    blank=True,
    validators=[
        RegexValidator(
            regex=r'^\d{8,12}$',
            message='El teléfono debe contener solo números y tener entre 8 y 12 dígitos.'
        )
    ]
)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre



class Zona(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=80)
    orden = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        ordering = ['sucursal', 'orden', 'nombre']

    def __str__(self):
        return f"{self.sucursal.nombre} - {self.nombre}"


class Maquina(models.Model):
    """
    Modelo para máquinas tragamonedas
    """
    is_active = models.BooleanField(default=True)

    ESTADO_CHOICES = [
        ('Operativa', 'Operativa'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Retirada', 'Retirada'),
    ]
    
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='maquinas',
        verbose_name='Sucursal'
    )
    zona = models.ForeignKey(
        Zona,
        on_delete=models.CASCADE,
        related_name='maquinas',
        verbose_name='Zona'
    )
    numero_maquina = models.IntegerField(verbose_name='Número de Máquina')
    codigo_interno = models.CharField(max_length=80, blank=True, verbose_name='Código Interno')
    nombre_juego = models.CharField(max_length=120, verbose_name='Nombre del Juego')
    modelo = models.CharField(max_length=80, blank=True, verbose_name='Modelo')
    numero_serie = models.CharField(max_length=120, blank=True, verbose_name='Número de Serie')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Operativa',
        verbose_name='Estado'
    )
    ubicacion_detalle = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Detalle de Ubicación'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    def __str__(self):
        return f"{self.sucursal.nombre} / {self.zona.nombre} / M{self.numero_maquina:02d} - {self.nombre_juego}"

    class Meta:
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        ordering = ['sucursal', 'zona', 'numero_maquina']
        unique_together = ['zona', 'numero_maquina']

    def clean(self):
        super().clean()
        if self.zona_id and self.sucursal_id:
            if self.zona.sucursal_id != self.sucursal_id:
                raise ValidationError(
                    {'sucursal': 'La sucursal debe coincidir con la sucursal de la zona seleccionada.'}

                )

class Turno(models.Model):
    """
    Modelo para turnos de trabajo
    """
    TIPO_TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
        ('Noche', 'Noche'),
    ]
    
    ESTADO_CHOICES = [
        ('Abierto', 'Abierto'),
        ('Cerrado', 'Cerrado'),
    ]
    
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='turnos',
        verbose_name='Sucursal'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='turnos',
        verbose_name='Usuario'
    )
    fecha = models.DateField(verbose_name='Fecha')
    tipo_turno = models.CharField(
        max_length=20,
        choices=TIPO_TURNO_CHOICES,
        verbose_name='Tipo de Turno'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Abierto',
        verbose_name='Estado'
    )
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    total_cierre = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total de Cierre'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-fecha', '-created_at']
    
    def __str__(self):
        return f"{self.sucursal.nombre} - {self.fecha} ({self.tipo_turno})"
    
    def clean(self):
        """
        Validar que no haya más de un turno abierto por usuario
        """
        if not self.usuario_id:
            return
        
        if self.estado == 'Abierto':
            turnos_abiertos = Turno.objects.filter(
                usuario=self.usuario,
                estado='Abierto'
            ).exclude(pk=self.pk)
            
            if turnos_abiertos.exists():
                raise ValidationError(
                    'Ya tiene un turno abierto. Debe cerrarlo antes de abrir uno nuevo.'
                )


class LecturaMaquina(models.Model):
    """
    Modelo para lecturas de máquinas en cada turno
    """
    turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Turno'
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Máquina'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Sucursal'
    )
    zona = models.ForeignKey(
        Zona,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Zona'
    )
    numero_maquina = models.IntegerField(verbose_name='Número de Máquina')
    nombre_juego = models.CharField(max_length=120, verbose_name='Nombre del Juego')
    
    # Campos de datos de la máquina
    entrada = models.IntegerField(verbose_name='Entrada')
    salida = models.IntegerField(verbose_name='Salida')
    total = models.IntegerField(verbose_name='Total')
    
    nota = models.CharField(max_length=255, blank=True, verbose_name='Nota')
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Usuario'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    
    class Meta:
        verbose_name = 'Lectura de Máquina'
        verbose_name_plural = 'Lecturas de Máquinas'
        ordering = ['-fecha_registro']


    def __str__(self):
        return f"Lectura {self.numero_maquina} - {self.nombre_juego} ({self.fecha_registro})"

    def clean(self):
        """
        No permitir más de una lectura de la misma máquina en el mismo turno.
        """
        super().clean()
        if self.turno_id and self.maquina_id:
            existe = LecturaMaquina.objects.filter(
                turno=self.turno,
                maquina=self.maquina
            ).exclude(pk=self.pk).exists()
            if existe:
                raise ValidationError(
                    'Ya existe una lectura registrada para esta máquina en este turno.'
                )

    def save(self, *args, **kwargs):
        """
        Guardar datos redundantes para facilitar reportes
        """
        if self.maquina:
            self.numero_maquina = self.maquina.numero_maquina
            self.nombre_juego = self.maquina.nombre_juego
            self.sucursal = self.maquina.sucursal
            self.zona = self.maquina.zona
        super().save(*args, **kwargs)