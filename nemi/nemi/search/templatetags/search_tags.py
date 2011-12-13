
from django import template

from decimal import Decimal

register = template.Library()

@register.filter
def decimal_format(num):
    if isinstance(num, Decimal):
        nv = str(num).rstrip('0')
        decimal_index = nv.rfind('.')
        if len(nv) == 1 and decimal_index != -1:
            return '0'
        elif decimal_index == len(nv) - 1:
            return nv[0:len(nv) - 1]
        else:
            return nv;
    else:
        return num

decimal_format.is_safe = True