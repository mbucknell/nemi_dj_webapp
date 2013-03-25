
from django import template
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.db.models.query import QuerySet

from ..models import HelpContent

register = template.Library()

@register.filter(name="get_help_content")
def get_help_content(help_qs, name):
    ''' 
    Return a HelpContent object with the field_name matching name. If
    the object is in help_qs. If help_qs is not a queryset or if it doesn't
    contain a field_name attribute return None. If an object matching name doesn't
    exist in help_qs, create a HelpContent object with field_name equal to name and
    a label field which is name with underscoreds turned into spaces and words capitalized.
    '''
    def _default_help(n):
        l = n.split('_')
        return HelpContent(field_name=name,
                           label=' '.join([a.capitalize() for a in l]))
    
    if isinstance(help_qs, QuerySet):
        try:
            return help_qs.get(field_name=name)
        except ObjectDoesNotExist:
            return _default_help(name)
        except FieldError:
            return None
        
    else:
        return None