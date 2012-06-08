'''
Created on Mar 15, 2012

@author: mbucknel
'''

# standard python packages
import types

def _get_choice_select(field):
    '''Returns the visible choice from the ChoiceField field parameter. The field must in a form
    be a bound field. The function assumes choice values are integer or string and retrieves
    the value kind from the second element in the choices list. This allows for an all or None
    selection as the first.
    '''
    if type(field.field.choices[1][0]) is types.IntType:
        return dict(field.field.choices).get(int(field.data))
    return dict(field.field.choices).get(field.data)

def get_criteria(field):
    '''Returns a tuple if the field value is not 'all', where the first element is the label
    of field and the second element is the visible choice for field.
    Assumes that the field is a ChoiceField and must be field in a form.
    '''
    if field.data == 'all':
        return None
    else:
        return (field.label, _get_choice_select(field))
    
def get_criteria_from_field_data(form, field_name, label_override=None ):
    '''Returns a tuple representing field_name's label and data from form.
    If the field's data value is none, the function returns None.
    '''
    if form.cleaned_data[field_name] == None:
        return None
    
    else:
        if label_override == None:
            return (form[field_name].label, form.cleaned_data[field_name])
        else:
            return (label_override, form.cleaned_data[field_name])
            
    
def get_multi_choice(form, name):
    ''' Returns the list of selected choices in a MultipleChoiceField. The form must be validated and the
    field is identified by name. If all are selected an empty list is returned.
    This function works for choice field values which are integer or string.
    '''
    choice_dict = dict(form[name].field.choices)
    if len(form.cleaned_data[name]) == len(choice_dict):
        return []
    else:
        if type(choice_dict.keys()[0]) is types.IntType:
            return [choice_dict.get(int(k)) for k in form.cleaned_data[name]]
        else:
            return [choice_dict.get(k) for k in form.cleaned_data[name]]
    
