# control/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def getattribute(obj, attr):
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None

@register.filter
def rtp_pct(entrada, salida):
    """Calcula RTP del local = (entrada - salida) / entrada * 100.
    Uso: {{ l.entrada_dia|rtp_pct:l.salida_dia }}
    """
    try:
        entrada = int(entrada or 0)
        salida = int(salida or 0)
        if entrada <= 0:
            return 0
        return round((entrada - salida) / entrada * 100, 1)
    except (TypeError, ZeroDivisionError):
        return 0


@register.filter
def get_ef(cz, key):
    """Retorna el valor del campo ef_XXXX o monedas_monto de un CuadraturaZona."""
    if cz is None:
        return 0
    field = "monedas_monto" if key == "monedas" else f"ef_{key}"
    return getattr(cz, field, 0) or 0