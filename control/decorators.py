from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*roles):
    """
    Permite acceso solo a los roles indicados.
    Acepta tanto lista como argumentos separados:
      @role_required('admin', 'gerente')
      @role_required(*ROLES_DASHBOARD)
    """
    # Compatibilidad: si se pasa una lista como primer arg (@role_required(["a","b"]))
    if len(roles) == 1 and isinstance(roles[0], (list, tuple)):
        roles = tuple(roles[0])

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('control:login')
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def readonly_for(*readonly_roles):
    """
    Bloquea POST para ciertos roles (solo lectura).
    @readonly_for(*ROLES_READONLY)
    """
    if len(readonly_roles) == 1 and isinstance(readonly_roles[0], (list, tuple)):
        readonly_roles = tuple(readonly_roles[0])

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('control:login')
            if request.user.role in readonly_roles and request.method == 'POST':
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── Grupos de roles ────────────────────────────────────────────
ROLES_DASHBOARD   = ('admin',)
ROLES_TURNO       = ('admin', 'encargado', 'asistente',)
ROLES_OPERACIONES = ('admin', 'gerente', 'supervisor', 'encargado','asistente',)
ROLES_REGISTRO    = ('admin', 'gerente', 'supervisor', 'encargado', 'asistente',)
ROLES_RECAUDACION = ('admin',)
ROLES_CONTROLES   = ('admin', 'gerente', 'supervisor',)
ROLES_CONFIG_VER  = ('admin', 'tecnico', 'gerente', 'supervisor', 'encargado',)
ROLES_CONFIG_EDIT = ('admin', 'tecnico',)
ROLES_USUARIOS    = ('admin',)
ROLES_VER_USUARIOS    = ('admin', "gerente", "supervisor",)
ROLES_READONLY    = ('supervisor', 'encargado',)
ROLES_CUADRATURA  = ('admin', 'gerente', 'supervisor','encargado')
ROLES_CUADRATURA_DIARIA  = ('admin', 'encargado')
ROLES_CUADRATURA_ZONA  = ('admin','encargado', 'asistente',)
