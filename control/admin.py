from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sucursal, Zona, Maquina, Turno, LecturaMaquina


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'nombre', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'nombre', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('nombre', 'role')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('nombre', 'role')}),
    )


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'telefono', 'created_at']
    search_fields = ['nombre', 'direccion']


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sucursal', 'orden', 'created_at']
    list_filter = ['sucursal']
    search_fields = ['nombre', 'sucursal__nombre']


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['numero_maquina', 'nombre_juego', 'sucursal', 'zona', 'estado']
    list_filter = ['sucursal', 'zona', 'estado']
    search_fields = ['numero_maquina', 'nombre_juego', 'codigo_interno']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sucursal', 'usuario', 'fecha', 'tipo_turno', 'estado', 'total_cierre')
    list_filter = ('sucursal', 'tipo_turno', 'estado', 'fecha')
    search_fields = ('sucursal__nombre', 'usuario__username', 'usuario__nombre')
    date_hierarchy = 'fecha'


@admin.register(LecturaMaquina)
class LecturaMaquinaAdmin(admin.ModelAdmin):
    list_display = ['numero_maquina', 'nombre_juego', 'entrada', 'salida', 'total', 'usuario', 'fecha_registro']
    list_filter = ['sucursal', 'zona', 'fecha_registro']
    search_fields = ['nombre_juego', 'numero_maquina', 'usuario__nombre']
    date_hierarchy = 'fecha_registro'
