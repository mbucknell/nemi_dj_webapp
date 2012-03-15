
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from decimal import Decimal


register = template.Library()

@register.filter(name='decimal_format')
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

@register.filter(name='obey_linefeeds')
@stringfilter
def obey_linefeeds(data, autoescape=None):
    '''Returns data with <br /> substituted for any line feeds.
    Filter correctly handles autoescaping.
    '''
    #If auto escape is used, we will need to escape the data string.
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
        
    lines = data.splitlines()
    if lines:
        result = esc(lines[0])
        i = 1
        while (i < len(lines)):
            result += '<br />%s' % esc(lines[i])
            i += 1
        
        return mark_safe(result)
    else:
        return data
    
obey_linefeeds.needs_autoescape = True

        