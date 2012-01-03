
from django import template

from decimal import Decimal

register = template.Library()

@register.filter
def decimal_format(num):
    ''' Returns a normalized decimal number with no trailing zeros and
    if the decimal number has no fraction part returns only the integer part
    with no decimal point.
    '''
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

## Set flag to indicate that the function does not introduce any HTML unsafe characters.
decimal_format.is_safe = True