from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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
    """
    Modelo para sucursales/locales
    """
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    telefono = models.CharField(max_length=50, blank=True, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Zona(models.Model):
    """
    Modelo para zonas dentro de sucursales
    """
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='zonas',
        verbose_name='Sucursal'
    )
    nombre = models.CharField(max_length=80, verbose_name='Nombre')
    orden = models.SmallIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
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
    
    class Meta:
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        ordering = ['sucursal', 'zona', 'numero_maquina']
        unique_together = ['zona', 'numero_maquina']
    
    def __str__(self):
        return f"{self.sucursal.nombre} / {self.zona.nombre} / M{self.numero_maquina:02d} - {self.nombre_juego}"


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
