'''
Created on Feb 10, 2012

@author: mbucknel
'''

from django.conf import settings
from django import template

register = template.Library()

@register.filter(name='verbose_help')
def verbose_help(field):
    try:
        return field.form.fields[field.name].verbose_help
    except AttributeError:
        return settings.TEMPLATE_STRING_IF_INVALID
    
verbose_help.is_safe = True
    