from .menu import MENU


def notificacion_recaudacion(request):
    """
    Inyecta notif_informes al contexto para encargado y asistente.
    Muestra solo informes reclamados por el turno encargado activo de su sucursal.
    """
    if not request.user.is_authenticated:
        return {}
    if request.user.role not in ('encargado', 'asistente'):
        return {}

    sucursal_id = request.session.get('sucursal_activa_id')
    if not sucursal_id:
        return {}

    from control.models import Turno, InformeRecaudacion

    turno_encargado = Turno.objects.filter(
        sucursal_id=sucursal_id,
        estado='Abierto',
        usuario__role='encargado',
    ).first()

    if not turno_encargado:
        return {}

    informes = list(
        InformeRecaudacion.objects
        .filter(sucursal_id=sucursal_id, notif_turno=turno_encargado, notificacion_consumida=False)
        .select_related('sucursal')
    )

    if not informes:
        return {}

    return {'notif_informes': informes}


def sidebar_menu(request):

    if not request.user.is_authenticated:
        return {}

    role = request.user.role
    menu_filtered = []

    for section in MENU:

        items = []

        for item in section["items"]:
            if role in item["roles"]:
                items.append(item)

        if items:
            menu_filtered.append({
                "section": section["section"],
                "items": items
            })

    return {
        "sidebar_menu": menu_filtered
    }