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
def get_ef(cz, key):
    """Retorna el valor del campo ef_XXXX o monedas_monto de un CuadraturaZona."""
    if cz is None:
        return 0
    field = "monedas_monto" if key == "monedas" else f"ef_{key}"
    return getattr(cz, field, 0) or 0