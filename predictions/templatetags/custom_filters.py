from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def is_string(value):
    """Check if value is a string"""
    return isinstance(value, str)

@register.filter
def percentage(value, decimals=1):
    """Convert decimal to percentage"""
    try:
        return f"{float(value)*100:.{decimals}f}%"
    except (ValueError, TypeError):
        return value

@register.filter(name='split')
@stringfilter
def split(value, delimiter=','):
    """Split a string by the given delimiter"""
    return [item.strip() for item in value.split(delimiter) if item.strip()]
@register.filter(name='strip')
@stringfilter
def strip_filter(value):
    """Remove leading and trailing whitespace"""
    return value.strip()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value