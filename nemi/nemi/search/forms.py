
from django.forms import Form, ChoiceField, MultipleChoiceField, CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from models import MethodVW
    
class GeneralSearchForm(Form):
    
        media_name = ChoiceField()
        source = ChoiceField()
        method_number = ChoiceField()
        instrumentation = ChoiceField()
        method_subcategory = ChoiceField()
        method_types = MultipleChoiceField(widget=CheckboxSelectMultiple())
        
        def __init__(self, *args, **kwargs):
            def _choice_cmp(a,b):
                if a[1] < b[1]:
                    return -1
                elif a[1] > b[1]:
                    return 1
                else:
                    return 0
                
            super(GeneralSearchForm, self).__init__(*args, **kwargs)
            
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
            
            mn_qs = qs.values_list('method_id', 'source_method_identifier', 'method_source').distinct()
            
            method_number_choices = [(method_id, mark_safe('%s (%s)' %(identifier, source))) for (method_id, identifier, source) in mn_qs]
            method_number_choices.sort(cmp=_choice_cmp)
            self.fields['method_number'].choices = [(u'all', u'Any')] + method_number_choices
              
            inst_qs = qs.values_list('instrumentation_id', 'instrumentation_description').distinct().order_by('instrumentation_description')
            self.fields['instrumentation'].choices = [(u'all', u'Any')] + [(i_id, id_descr) for (i_id, id_descr) in inst_qs]
            
            sub_qs = qs.values_list('method_subcategory_id', 'method_subcategory').distinct().order_by('method_subcategory')
            self.fields['method_subcategory'].choices = [(u'all', u'Any')] + [(s_id, s) for (s_id, s) in sub_qs]
            
            mt_qs = qs.values_list('method_type_id', 'method_type_desc').distinct().order_by('method_type_desc')
            self.fields['method_types'].choices = [(t_id, desc) for (t_id, desc) in mt_qs]  
            self.fields['method_types'].initial = [t_id for (t_id, desc) in mt_qs] 
            
    
