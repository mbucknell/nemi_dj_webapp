
from django import template

from ..models import HelpContent

register = template.Library()

@register.filter(name="get_help_content")
def get_help_content(help_dict, name):
    ''' 
    Return an object with at least two attributes, field_name and label. 
    If help_dict is a dictionary containing a key value matching name with a value that has an object with the field_name and label attribute
    then that object will be returned. If none of those conditions is met,
    the function will return a HelpContent object with two attributes, field_name and label with field_name matching name and label containing
    name with underscores replaced by spaces and words capitalized.
    '''
    def _default_help(n):
        l = n.split('_')
        return HelpContent(field_name=name,
                      label=' '.join([a.capitalize() for a in l]))
    
    if isinstance(help_dict, dict):
        content = help_dict.get(name, _default_help(name))
        if hasattr(content, 'label') and hasattr(content, 'field_name'):
            return content
        else:
            return _default_help(name);
        
    else:
        return _default_help(name)