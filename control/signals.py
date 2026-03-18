"""
Señales de audit log.
Captura automáticamente creates / edits / deletes de los modelos clave,
y los eventos de login / logout de Django.
"""
import threading

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

# ── Modelos auditados → etiqueta legible ─────────────────────────────────────
MODELOS = {
    'LecturaMaquina':       'Lectura de Máquina',
    'Turno':                'Turno',
    'CuadraturaCajaDiaria': 'Cuadratura de Caja',
    'CuadraturaZona':       'Cuadratura de Zona',
    'Maquina':              'Máquina',
    'Zona':                 'Zona',
    'Sucursal':             'Sucursal',
    'Usuario':              'Usuario',
    'CicloRecaudacion':     'Ciclo de Recaudación',
    'ControlLecturas':      'Control de Lecturas',
}

# Campos técnicos/automáticos que no aportan valor en el diff
CAMPOS_IGNORADOS = frozenset({
    'id', 'fecha_registro', 'creado_el', 'actualizado_el',
    'created_at', 'actualizado', 'last_login', 'password',
})

# Thread-local: guarda la instancia anterior para calcular el diff en ediciones
_pre = threading.local()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_request():
    from control.middleware import get_current_request
    return get_current_request()


def _contexto(request=None):
    """Devuelve (usuario, nombre, sucursal, nombre_suc, ip) del request."""
    usuario = nombre = sucursal = nombre_suc = ip = None
    if request is None:
        request = _get_request()
    if request and getattr(request, 'user', None) and request.user.is_authenticated:
        usuario = request.user
        nombre = getattr(usuario, 'nombre', '') or usuario.username

        suc_id = request.session.get('sucursal_activa_id')
        if suc_id:
            try:
                from control.models import Sucursal
                sucursal = Sucursal.objects.get(pk=suc_id)
                nombre_suc = sucursal.nombre
            except Exception:
                pass

        if not sucursal:
            suc = getattr(usuario, 'sucursales', None)
            if suc:
                s = suc.first()
                if s:
                    sucursal, nombre_suc = s, s.nombre

        x_fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = x_fwd.split(',')[0].strip() if x_fwd else request.META.get('REMOTE_ADDR')

    return usuario, nombre, sucursal, nombre_suc, ip


def _diff(old_obj, new_obj):
    """Retorna dict de campos modificados: {campo: {antes, despues}}."""
    cambios = {}
    for field in new_obj._meta.concrete_fields:
        name = field.name
        if name in CAMPOS_IGNORADOS:
            continue
        old_val = getattr(old_obj, name, None)
        new_val = getattr(new_obj, name, None)
        if old_val != new_val:
            cambios[name] = {
                'antes':   str(old_val) if old_val is not None else None,
                'despues': str(new_val) if new_val is not None else None,
            }
    return cambios


def _log(tipo, modulo, objeto=None, descripcion='', detalles=None, request=None):
    """Crea un RegistroActividad. Nunca propaga excepciones al flujo principal."""
    try:
        from control.models import RegistroActividad
        usuario, nombre, sucursal, nombre_suc, ip = _contexto(request)
        obj_id  = str(objeto.pk) if objeto and hasattr(objeto, 'pk') and objeto.pk else ''
        obj_str = str(objeto)[:300] if objeto else ''

        RegistroActividad.objects.create(
            usuario=usuario,
            nombre_usuario=nombre or '',
            sucursal=sucursal,
            nombre_sucursal=nombre_suc or '',
            tipo=tipo,
            modulo=modulo,
            objeto_id=obj_id,
            objeto_str=obj_str,
            descripcion=descripcion,
            detalles=detalles or None,
            ip=ip,
        )
    except Exception:
        pass


# ── Signals de modelos ────────────────────────────────────────────────────────

@receiver(pre_save)
def _capturar_antes(sender, instance, **kwargs):
    """Guarda el estado previo del objeto para calcular el diff en post_save."""
    if sender.__name__ not in MODELOS:
        return
    if instance.pk:
        try:
            _pre.old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            _pre.old = None
    else:
        _pre.old = None


@receiver(post_save)
def _post_save(sender, instance, created, **kwargs):
    nombre = sender.__name__
    if nombre not in MODELOS:
        return
    modulo = MODELOS[nombre]
    if created:
        _log('CREAR', modulo, instance, descripcion=f'Nuevo registro: {instance}')
    else:
        old = getattr(_pre, 'old', None)
        cambios = _diff(old, instance) if old else None
        _log(
            'EDITAR', modulo, instance,
            descripcion=f'Editado: {instance}',
            detalles=cambios if cambios else None,
        )


@receiver(post_delete)
def _post_delete(sender, instance, **kwargs):
    nombre = sender.__name__
    if nombre not in MODELOS:
        return
    _log('ELIMINAR', MODELOS[nombre], instance, descripcion=f'Eliminado: {instance}')


# ── Login / Logout ────────────────────────────────────────────────────────────

@receiver(user_logged_in)
def _login(sender, request, user, **kwargs):
    nombre = getattr(user, 'nombre', '') or user.username
    x_fwd  = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip     = x_fwd.split(',')[0].strip() if x_fwd else request.META.get('REMOTE_ADDR')
    try:
        from control.models import RegistroActividad
        RegistroActividad.objects.create(
            usuario=user,
            nombre_usuario=nombre,
            tipo='LOGIN',
            modulo='Sesión',
            objeto_str=user.username,
            descripcion=f'Inicio de sesión: {nombre}',
            ip=ip,
        )
    except Exception:
        pass


@receiver(user_logged_out)
def _logout(sender, request, user, **kwargs):
    if not user:
        return
    nombre = getattr(user, 'nombre', '') or user.username
    try:
        from control.models import RegistroActividad
        RegistroActividad.objects.create(
            usuario=user,
            nombre_usuario=nombre,
            tipo='LOGOUT',
            modulo='Sesión',
            objeto_str=user.username,
            descripcion=f'Cierre de sesión: {nombre}',
        )
    except Exception:
        pass
