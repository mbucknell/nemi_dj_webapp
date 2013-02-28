''' This module contains the forms needed to implement the NEMI search pages '''

from django.forms import Form, ChoiceField, MultipleChoiceField, CheckboxSelectMultiple, RadioSelect, CharField, TextInput

from models import RegulationRef, RegulatoryMethodReport

def _choice_cmp(a,b):
    ''' Returns -1, 1, or 0 by comparing the 2nd element in a with b.
    This function is meant to be used on choice tuples
    and is used to sort choice sets.
    '''
    if a[1] < b[1]:
        return -1
    elif a[1] > b[1]:
        return 1
    else:
        return 0
    
def _method_source_choice_set(qs):
    ''' Returns a list of choice tuples representing the available method sources in
    the query set qs.
    The function collapses sources from  EPA, USGS, and DOE. All others appear as in the table.
    '''
    sc_qs = qs.values_list('method_source', 'method_source_name').distinct().exclude(method_source__contains='EPA').exclude(method_source__contains='USGS').exclude(method_source__startswith='DOE')
    source_choices = [(source, name) for (source, name) in sc_qs]
    if qs.filter(method_source__contains='EPA').exists():
        source_choices.append((u'EPA', u'US Environmental Protection Agency'))
    if qs.filter(method_source__contains='USGS').exists():
        source_choices.append((u'USGS', u'US Geological Survey'))
    if qs.filter(method_source__startswith=u'DOE').exists():
        source_choices.append((u'DOE', u'US Department of Energy'))
    source_choices.sort(cmp=_choice_cmp)
    
    return source_choices

class CheckBoxMultipleChoiceField(MultipleChoiceField):
    widget = CheckboxSelectMultiple()
    error_messages = {'required' : 'Please select at least one method type'}
    

class RegulatorySearchForm(Form):
    '''Extends the Form class to implement the Regulatory Search form.
    Contains choice fields used to filter the search of the RegulationRef table.
    The choice fields that are not static are extracted at instantiation from the database.'''
        
    analyte_kind = ChoiceField(choices=[('name', 'Name'), ('code', 'Code')],
                               initial='name',
                               widget=RadioSelect(attrs={'id' : 'analyte-search-kind'}))
    analyte_value = CharField(widget=TextInput(attrs={'id' : 'analyte-search-value'}))
    regulation = ChoiceField()
    
    def __init__(self, *args, **kwargs):
        super(RegulatorySearchForm, self).__init__(*args, **kwargs)
        
        #Find regulations
        qs = RegulationRef.objects.values_list('regulation', 'regulation_name').order_by('regulation_name').distinct()
        self.fields['regulation'].choices = [(u'all', u'Any')] + [(reg, name) for (reg, name) in qs]
        
class TabularSearchForm(Form):
    '''Extends the Form class to implement the Tabular Regulatory Search form.
    Contains choice fields used to filter the search of the RegulatoryMethodReport table.
    The choice fields that are not static are extracted at instantiation from the database.'''
        
    analyte = ChoiceField()
    
    def __init__(self, *args, **kwargs):
        super(TabularSearchForm, self).__init__(*args, **kwargs)
        
        qs = RegulatoryMethodReport.objects.values_list('analyte_name', flat=True).order_by('analyte_name')
        self.fields['analyte'].choices = [(u'all', u'Any')] + [(name, name) for name in qs]
        
