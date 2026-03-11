from django.shortcuts import redirect
from django.urls import reverse


# URLs que el encargado puede visitar SIN haber seleccionado sucursal
URLS_LIBRES = {
    'control:login',
    'control:logout',
    'control:seleccionar_sucursal',
}


class SucursalEncargadoMiddleware:
    """
    Si el usuario es encargado/asistente/supervisor y tiene más de una sucursal,
    obliga a pasar por la pantalla de selección de sucursal antes de continuar.
    La sucursal elegida se guarda en request.session['sucursal_activa_id'].
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

        # Solo usuarios autenticados con rol que requiere selección
        if not user.is_authenticated:
            return False
        if user.role not in self.ROLES_CON_SELECCION:
            return False

        # Si ya seleccionó sucursal, no interrumpir
        if request.session.get('sucursal_activa_id'):
            return False

        # Si ya está en la pantalla de selección o en login/logout, no interrumpir
        seleccion_url = reverse('control:seleccionar_sucursal')
        login_url     = reverse('control:login')
        logout_url    = reverse('control:logout')
        if request.path in (seleccion_url, login_url, logout_url):
            return False

        # Si tiene más de una sucursal → obligar selección
        return user.sucursales.filter(is_active=True).count() > 1
