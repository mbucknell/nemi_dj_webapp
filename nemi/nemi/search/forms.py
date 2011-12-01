''' This module contains the forms needed to implement the NEMI search pages '''

from django.forms import Form, ChoiceField, MultipleChoiceField, CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from models import MethodVW
    
class GeneralSearchForm(Form):
    ''' This class extends the django Form class. The form is used to represent the general search form
    and contains choice fields used to filter the search of the MethodVW data. The choice field values 
    are determined from the MethodVW table.
    '''
    
    media_name = ChoiceField()
    source = ChoiceField()
    method_number = ChoiceField()
    instrumentation = ChoiceField()
    method_subcategory = ChoiceField()
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                                       error_messages={'required' : 'Please select at least one method type'})
        
    def __init__(self, *args, **kwargs):
        '''Extends the parent instantiona method to extract the choice values
        from the current contents of the MethodVW table.
        '''
        def _choice_cmp(a,b):
            ''' Comparision function meant to be used on choice tubles
            and is used to sort choice sets.
            '''
            if a[1] < b[1]:
                return -1
            elif a[1] > b[1]:
                return 1
            else:
                return 0
            
        super(GeneralSearchForm, self).__init__(*args, **kwargs)
        
        # Find media name choice set.
        qs = MethodVW.objects.all()
        self.fields['media_name'].choices = [(u'all', u'Any')] + [(m['media_name'], m['media_name'].capitalize()) 
                                                                for m in qs.values('media_name').distinct().order_by('media_name')]

        # Media source choices, need to collapse, EPA, USGS, and DOE, all others appear as in the table.
        sc_qs = qs.values_list('method_source', 'method_source_name').distinct().exclude(method_source__contains='EPA').exclude(method_source__contains='USGS').exclude(method_source__startswith='DOE')
        source_choices = [(source, name) for (source, name) in sc_qs]
        if qs.filter(method_source__contains='EPA').exists():
            source_choices.append((u'EPA', u'US Environmental Protection Agency'))
        if qs.filter(method_source__contains='USGS').exists():
            source_choices.append((u'USGS', u'US Geological Survey'))
        if qs.filter(method_source__startswith=u'DOE').exists():
            source_choices.append((u'DOE', u'US Department of Energy'))
        source_choices.sort(cmp=_choice_cmp)
        self.fields['source'].choices = [(u'all', u'Any')] + source_choices
        
        #Method number choices. Since the identifier and source fields may contain html formatting information, 
        #this field is marked as safe so that the html is not escaped.
        mn_qs = qs.values_list('method_id', 'source_method_identifier', 'method_source').distinct()
        method_number_choices = [(method_id, mark_safe('%s (%s)' %(identifier, source))) for (method_id, identifier, source) in mn_qs]
        method_number_choices.sort(cmp=_choice_cmp)
        self.fields['method_number'].choices = [(u'all', u'Any')] + method_number_choices
          
        #Instrumentation description choices
        inst_qs = qs.values_list('instrumentation_id', 'instrumentation_description').distinct().order_by('instrumentation_description')
        self.fields['instrumentation'].choices = [(u'all', u'Any')] + [(i_id, id_descr) for (i_id, id_descr) in inst_qs]
        
        #Method Subcategory choices
        sub_qs = qs.values_list('method_subcategory_id', 'method_subcategory').distinct().order_by('method_subcategory')
        self.fields['method_subcategory'].choices = [(u'all', u'Any')] + [(s_id, s) for (s_id, s) in sub_qs]
        
        #Method type choice fields. We initialize this to all values being set.
        mt_qs = qs.values_list('method_type_id', 'method_type_desc').distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(t_id, desc) for (t_id, desc) in mt_qs]  
        self.fields['method_types'].initial = [t_id for (t_id, desc) in mt_qs] 
