import threading

from django.shortcuts import redirect
from django.urls import reverse
from django.core.cache import cache

# ── Thread-local: expone el request actual a los signals ──────────────────────
_current_request_local = threading.local()


def get_current_request():
    return getattr(_current_request_local, 'request', None)


class CurrentRequestMiddleware:
    """
    Almacena el request actual en thread-local para que los signals de audit
    puedan identificar al usuario que disparó la acción.
    Debe ir DESPUÉS de AuthenticationMiddleware en MIDDLEWARE.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _current_request_local.request = request
        try:
            return self.get_response(request)
        finally:
            _current_request_local.request = None


class SucursalEncargadoMiddleware:
    """
    Encargado: bloquea navegación hasta que tenga sucursal activa Y turno abierto.
    Asistente: bloquea navegación hasta que tenga sucursal activa (si tiene 2+).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._debe_ir_a_seleccionar_turno(request):
            return redirect(reverse('control:seleccionar_turno'))
        if self._debe_ir_a_seleccionar_sucursal(request):
            return redirect(reverse('control:seleccionar_sucursal'))
        return self.get_response(request)

    def _debe_ir_a_seleccionar_turno(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'encargado':
            return False
        try:
            exempt = {
                reverse('control:seleccionar_turno'),
                reverse('control:login'),
                reverse('control:logout'),
            }
        except Exception:
            return False
        if request.path in exempt:
            return False
        # Permitir que encargados entren como asistente
        try:
            from django.urls import resolve
            match = resolve(request.path)
            if match.url_name == 'entrar_como_asistente':
                return False
        except Exception:
            pass
        # Sin sucursal activa → debe ir a seleccionar_turno
        if not request.session.get('sucursal_activa_id'):
            return True
        # Encargado entró como asistente de otro turno → dejar pasar
        if request.session.get('modo_asistente_turno_id'):
            return False
        # Con sucursal pero sin turno abierto propio → debe ir a seleccionar_turno
        from control.models import Turno
        return not Turno.objects.filter(usuario=user, estado='Abierto').exists()

    def _debe_ir_a_seleccionar_sucursal(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'asistente':
            return False
        if request.session.get('sucursal_activa_id'):
            return False
        try:
            exempt = {
                reverse('control:seleccionar_sucursal'),
                reverse('control:login'),
                reverse('control:logout'),
            }
        except Exception:
            return False
        if request.path in exempt:
            return False
        return user.sucursales.filter(is_active=True).count() > 1


class AlertaSesionCerradaMiddleware:
    """
    Intercepta el redirect 302 al login cuando un asistente fue desconectado
    forzosamente por quedarse sin asignaciones. Añade ?uid=<pk> a la URL
    para que login_view pueda mostrar la alerta correspondiente.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Solo interceptar redirects al login
        if response.status_code != 302:
            return response

        try:
            login_url = reverse("control:login")
        except Exception:
            return response

        location = response.get("Location", "")
        if not location.startswith(login_url):
            return response

        # Ya tiene uid → no modificar
        if "uid=" in location:
            return response

        # Buscar en caché si hay algún asistente con flag de cierre forzado
        try:
            from control.models import Usuario
            asistentes = Usuario.objects.filter(role="asistente").values_list("id", flat=True)
            for uid in asistentes:
                if cache.get(f"forzado_sin_asig_{uid}"):
                    sep = "&" if "?" in location else "?"
                    response["Location"] = f"{location}{sep}uid={uid}"
                    break
        except Exception:
            pass

        return response


class ErrorHandlerMiddleware:
    """
    Captura excepciones no manejadas y devuelve una respuesta limpia
    en vez de mostrar el traceback completo al usuario.
    Solo activo cuando DEBUG=False.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        from django.conf import settings
        if settings.DEBUG:
            return None
        from django.core.exceptions import PermissionDenied
        from django.http import Http404
        if isinstance(exception, (PermissionDenied, Http404)):
            return None  # Django maneja 403 y 404 de forma nativa
        import logging
        logger = logging.getLogger('django')
        logger.error(
            f"Excepción no manejada en {request.path}: {exception}",
            exc_info=True,
            extra={"request": request},
        )
        from django.shortcuts import render
        return render(request, "errors/500.html", status=500)