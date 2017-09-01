
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize
from django.utils.safestring import mark_safe

from decimal import Decimal
import re


register = template.Library()

@register.filter(name='decimal_format', is_safe=True)
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

@stringfilter
@register.filter(name='clickable_links')
def clickable_links(data):
    '''
    Returns data translated into clickable links. This is different from the Django provided
    urlize in two ways. One is the ref attribute in the 'a' tag is not set to nofollow. The
    second way is that data can contain more than one link as long as they are separated by
    "<br /> tag. The returned string will insert the <br /> tag between the clickable links.
    '''

    # The following line will find any <br> or <br/> tag with spaces within the tag and replace those varients with <br/>
    urlstr = re.sub('<br(>|/>)','<br/>', data.replace(' ', ''))
    urls = urlstr.split('<br/>')
    result = [urlize(u, autoescape=False) for u in urls]
    return mark_safe('<br />'.join(result))
