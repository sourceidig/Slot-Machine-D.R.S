# control/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def getattribute(obj, attr):
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None
