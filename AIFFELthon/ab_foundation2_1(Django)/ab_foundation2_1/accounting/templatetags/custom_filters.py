from django import template
import pprint

register = template.Library()

@register.filter(name='pprint')
def pprint_filter(value):
    if isinstance(value, dict) or isinstance(value, list):
        return pprint.pformat(value, indent=2, width=120)
    return value