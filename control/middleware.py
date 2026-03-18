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


# URLs que el encargado puede visitar SIN haber seleccionado sucursal
URLS_LIBRES = {
    'control:login',
    'control:logout',
    'control:seleccionar_sucursal',
}


class SucursalEncargadoMiddleware:
    """
    Si el usuario es encargado/asistente y tiene más de una sucursal,
    obliga a pasar por la pantalla de selección de sucursal antes de continuar.
    """

    ROLES_CON_SELECCION = ('encargado', 'asistente')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._debe_seleccionar(request):
            return redirect(reverse('control:seleccionar_sucursal'))
        return self.get_response(request)

    def _debe_seleccionar(self, request):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role not in self.ROLES_CON_SELECCION:
            return False
        if request.session.get('sucursal_activa_id'):
            return False
        seleccion_url = reverse('control:seleccionar_sucursal')
        login_url     = reverse('control:login')
        logout_url    = reverse('control:logout')
        if request.path in (seleccion_url, login_url, logout_url):
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
            return None  # Django muestra el traceback normal en desarrollo
        import logging
        logger = logging.getLogger('django')
        logger.error(
            f"Excepción no manejada en {request.path}: {exception}",
            exc_info=True,
            extra={"request": request},
        )
        # Devolver página de error genérica
        from django.http import HttpResponse
        return HttpResponse(
            "<h2>Ocurrió un error inesperado. Por favor intenta de nuevo.</h2>"
            "<p><a href='/'>Volver al inicio</a></p>",
            status=500
        )