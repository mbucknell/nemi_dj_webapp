''' This module contains the forms needed to implement the NEMI search pages '''

from django.forms import Form, ChoiceField, MultipleChoiceField, CheckboxSelectMultiple, RadioSelect, CharField, SelectMultiple, TextInput, HiddenInput
from django.utils.safestring import mark_safe
from models import MethodVW, AnalyteCodeVW, AnalyteCodeRel, MediaNameDOM, InstrumentationRef, MethodSubcategoryRef, MethodSourceRef, MethodAnalyteAllVW
from models import statisticalDesignObjective,statisticalItemType,relativeCostRef,statisticalSourceType, MediaNameDOM, statisticalTopics, statisticalAnalysisType
    
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
    
class GeneralSearchForm(Form):
    ''' Extends the Form class to implement the general search form
    and contains choice fields used to filter the search of the MethodVW data. The choice field values 
    are extracted from the MethodVW table.
    '''
    
    media_name = ChoiceField()
    source = ChoiceField()
    method_number = ChoiceField()
    instrumentation = ChoiceField()
    method_subcategory = ChoiceField()
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                                       error_messages={'required' : 'Please select at least one method type'})
        
    def __init__(self, *args, **kwargs):
        '''Extends the parent instantiation method to extract the choice values
        from the current contents of the MethodVW table.
        '''
     
        super(GeneralSearchForm, self).__init__(*args, **kwargs)
        
        # Find media name choice set.
        qs = MethodVW.objects.all()
        self.fields['media_name'].choices = [(u'all', u'Any')] + [(m['media_name'], m['media_name'].capitalize()) 
                                                                for m in qs.values('media_name').distinct().order_by('media_name')]

        # Find Media source choices
        self.fields['source'].choices = [(u'all', u'Any')] + _method_source_choice_set(qs)
        
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
        mt_qs = qs.values('method_type_desc', 'method_type_id').distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(d['method_type_id'], d['method_type_desc']) for d in mt_qs]  
        self.fields['method_types'].initial = [d['method_type_id'] for d in mt_qs]
        

        
class AnalyteSearchForm(Form):
    '''Extends the standard Form to implement the analyte search form. 
    The choice field selections are determined when the form is instantiated by querying the database
    for valid selections.
    '''
    analyte_kind = ChoiceField(choices=[('name', 'Name'), ('code', 'Code')],
                       initial='name',
                       widget=RadioSelect(attrs={'id' : 'analyte-search-kind'}))
    analyte_value = CharField(widget=TextInput(attrs={'id' : 'analyte-search-value'}))
    media_name = ChoiceField()
    source = ChoiceField()
    instrumentation = ChoiceField()
    method_subcategory = ChoiceField()
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                                       error_messages={'required' : 'Please select at least one method type'})
    
    def __init__(self, *args, **kwargs):
        ''' Extends the parent method to extract the choice values from the database.'''
        super(AnalyteSearchForm, self).__init__(*args, **kwargs)
        
        # Find media name choice set
        qs = MediaNameDOM.objects.order_by('media_name').values_list('media_name', flat=True)
        self.fields['media_name'].choices = [(u'all', u'Any')] + [(name, name.capitalize()) for name in qs]
        
        # Find method source choice set. Need to collapse, EPA, USGS, and DOE, all others appear as in the table
        self.fields['source'].choices = [(u'all', u'Any')] + _method_source_choice_set(MethodSourceRef.objects.all())
        
        #Instrumentation
        qs = InstrumentationRef.objects.order_by('instrumentation_description').values('instrumentation_id', 'instrumentation_description')
        self.fields['instrumentation'].choices = [(u'all', u'Any')] + [(d['instrumentation_id'], d['instrumentation_description']) for d in qs]
        
        #Find method subcategory choices
        qs = MethodSubcategoryRef.objects.filter(
                method_subcategory_id__in=[8, 2, 5, 1, 9, 4, 10]).order_by('method_subcategory').values('method_subcategory_id', 'method_subcategory')
        self.fields['method_subcategory'].choices = [(u'all', u'Any')] + [(d['method_subcategory_id'], d['method_subcategory']) for d in qs]
        
        # find method type choices and select all of them
        qs = MethodVW.objects.order_by('method_type_desc').values_list('method_type_desc', flat=True).distinct()
        self.fields['method_types'].choices = [(desc, desc) for desc in qs]
        self.fields['method_types'].initial = [desc for desc in qs]

                  
class AnalyteSelectForm(Form):
    ''' This class extends the standard Form to implement the analyte select form. This form
    allows the user to enter a partial string to and then see which analytes match that string.
    The analyte kind (by name or code) is set when the form is instantiated by setting the kind field. If
    the kind is not code, it is assumed to be name. If the selection field is not empty, the values_list is filled
    in by querying the database for analyte name/code that contain the string in the selection field.
    '''
    
    kind = CharField(widget=HiddenInput())
    selection = CharField()
    values_list = ChoiceField(widget=SelectMultiple(attrs={'id': 'values-list',
                                                           'size' : 20}))

    def __init__(self, *args, **kwargs):
        super(AnalyteSelectForm, self).__init__(*args, **kwargs)
        
        if 'selection' in self.data:
            value = self.data['selection']
            if value != "":
                if self.data['kind'] == 'code':
                    qs = AnalyteCodeVW.objects.filter(analyte_analyte_code__icontains=value).order_by('analyte_analyte_code').values_list('analyte_analyte_code', flat=True).distinct()
                
                else:
                    qs = AnalyteCodeRel.objects.filter(analyte_name__icontains=value).order_by('analyte_name').values_list('analyte_name', flat=True)
                
                self.fields['values_list'].choices=[(choice, choice) for choice in qs]    

class KeywordSearchForm(Form):
    
    ''' Extends the standard Form to implement the keyword search form. 
    '''
    keywords = CharField()
    
class MicrobiologicalSearchForm(Form):
    ''' Extends the Form class to implement the microbiological search form.
    Contains choice fields used to to filter the search of MethodAnalyteAllVw data.
    The choice field values are extracted from the MethodAnalytedAllVw view and the MethodVW view.
    '''
    
    analyte = ChoiceField(label="Analyte name (code)")
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                                       error_messages={'required' : 'Please select at least one method type'})
    
    def __init__(self, *args, **kwargs):
        ''' Extends the parent instantiation method to extract the choice values from the database.'''
        super(MicrobiologicalSearchForm, self).__init__(*args, **kwargs)
        
        #Find analytes
        qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact='5').values_list('analyte_name', 'analyte_code', 'analyte_id').distinct().order_by('analyte_name', 'analyte_code')
        self.fields['analyte'].choices = [(u'all', u'Any')] + [ (a_id, '%s (%s)' %(name, code)) for (name, code, a_id) in qs]
        
        qs = MethodVW.objects.filter(method_subcategory_id__exact='5').values_list('method_type_desc', flat=True).distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(m, m) for m in qs]
        self.fields['method_types'].initial = [m for m in qs]
        
class BiologicalSearchForm(Form):
    ''' Extends the Form class to implement the biological search form.
    Contains choice fields used to to filter the search of MethodAnalyteAllVw data.
    Some choice fields are static and the rest are extracted from the database.
    '''

    analyte_type = ChoiceField(choices=[(u'all', u'Any'), 
                                        (u'Algae', u'Algae'), 
                                        (u'Fish', u'Fish'), 
                                        (u'Macroinvertebrate', u'Macroinvertebrate')]
                               )
    waterbody_type = ChoiceField(choices=[(u'all', u'Any'),
                                          (u'Estuary', u'Estuary'),
                                          (u'Lake', u'Lake'),
                                          (u'Ocean', u'Ocean'),
                                          (u'River', u'River'),
                                          (u'Non-wadeable stream', u'Non-wadeable stream'),
                                          (u'Wadeable stream', u'Wadeable stream'),
                                          (u'Wetland', u'Wetland')]
                                 )
    gear_type = ChoiceField()
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                                       error_messages={'required' : 'Please select at least one method type'})

    def __init__(self, *args, **kwargs):
        super(BiologicalSearchForm, self).__init__(*args, **kwargs)
        
        #Get gear types
        qs = InstrumentationRef.objects.filter(instrumentation_id__range=(112, 121)).order_by('instrumentation_description').values_list('instrumentation_id', 'instrumentation_description')
        self.fields['gear_type'].choices = [(u'all', u'Any')] + [(i_id, desc) for (i_id, desc) in qs]
        
        # Get method types
        qs = MethodVW.objects.filter(method_subcategory_id__exact='7').values_list('method_type_desc', flat=True).distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(m, m) for m in qs]
        self.fields['method_types'].initial = [m for m in qs]
        
class ToxicitySearchForm(Form):
    '''Extends the Form class to implement the Toxicity Search form.
    Contains choice fields used to filter the search of the MethodAnalyteAllVW view.
    The choice fields that are not static are extracted at instantiation from the database.'''
    subcategory = ChoiceField()
    media = ChoiceField()
    matrix = ChoiceField(choices=[(u'all', 'Any'),
                                  (u'Freshwater', u'Freshwater'),
                                  (u'Saltwater', u'Saltwater'),
                                  (u'Both', u'Both')])
    method_types = MultipleChoiceField(widget=CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super(ToxicitySearchForm, self).__init__(*args, **kwargs)
        
        qs = MethodAnalyteAllVW.objects.filter(method_category__exact='TOXICITY ASSAY')

        # Get subcategory choices
        sub_qs = qs.values_list('method_subcategory', flat=True).distinct().order_by('method_subcategory')
        self.fields['subcategory'].choices = [(u'all', u'Any')] + [(s, s) for s in sub_qs]
        
        #Get media choices
        m_qs = qs.values_list('media_name', flat=True).distinct().order_by('media_name')
        self.fields['media'].choices = [(u'all', u'Any')] + [(m, m) for m in m_qs]
        
        #Get method types
        qs = MethodVW.objects.filter(method_category__exact='TOXICITY ASSAY').values_list('method_type_desc', flat=True).distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(m, m) for m in qs]
        self.fields['method_types'].initial = [m for m in qs]
        
class StatisticSearchForm(Form):
    ''' This class extends the django Form class. The form is used to represent the general search form
    and contains choice fields used to filter the search of the MethodVW data. The choice field values 
    are determined from the MethodVW table.
    '''

    item_type = ChoiceField()
    complexity = ChoiceField()
    analysis_type = ChoiceField()
    sponsor_type = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                error_messages={'required' : 'Please select at least one method type'})
#    design_or_data_analysis_objective = MultipleChoiceField(widget=CheckboxSelectMultiple(),
#                error_messages={'required' : 'Please select at least one method type'})
    media_emaphsized = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                error_messages={'required' : 'Please select at least one method type'})
    special_topics = MultipleChoiceField(widget=CheckboxSelectMultiple(),
                error_messages={'required' : 'Please select at least one method type'})
        
    def __init__(self, *args, **kwargs):
        '''Extends the parent instantiation method to extract the choice values
        from the current contents of the MethodVW table.
        '''
     
        super(StatisticSearchForm, self).__init__(*args, **kwargs)
        
        # Find media name choice set.
        design = statisticalDesignObjective.objects.all()
        item = statisticalItemType.objects.all()
        complex = relativeCostRef.objects.all()
        source = statisticalSourceType.objects.all()
        media = MediaNameDOM.objects.all()
        topics = statisticalTopics.objects.all()
        analysis = statisticalAnalysisType.objects.all()
        
#        #Statistical item type
        item_qs = item.values_list('stat_item_index', 'item').distinct().order_by('item')
        self.fields['item_type'].choices = [(u'all', u'Any')] + [(item_id, item_name) for (item_id, item_name) in item_qs]
              
#        #Complexity
        complex_qs = complex.values_list('relative_cost_id', 'relative_cost').distinct().order_by('relative_cost')
        self.fields['complexity'].choices = [(u'all', u'Any')] + [(com_id, com) for (com_id, com) in complex_qs]  # Should change this so it's only relative_cost_ids 13-15

        #Analysis
        analysis_qs = analysis.values_list('stat_analysis_index', 'analysis_type').distinct().order_by('stat_analysis_index')
        self.fields['analysis_type'].choices = [(u'all', u'Any')] + [(a_id, a) for (a_id, a) in analysis_qs]
        
        #Source type choice fields. We initialize this to all values being set.
        source_qs = source.values('stat_source_index', 'source').distinct().order_by('source')
        self.fields['sponsor_type'].choices = [(s['stat_source_index'], s['source']) for s in source_qs]  
        self.fields['sponsor_type'].initial = [s['stat_source_index'] for s in source_qs]         
        
##      #Statistical design objective - not sure why this won't work....
#        design_qs = design.values_list('stat_design_index', 'objective').distinct().order_by('objective')
#        self.fields['design_or_data_analysis_objective'].choices = [(d['stat_design_index'], d['objective']) for d in design_qs]
#        self.fields['design_or_data_analysis_objective'].initial = [d['stat_design_index'] for d in design_qs] 

        #Source type choice fields. We initialize this to all values being set.
        media_qs = media.values('media_id', 'media_name').distinct().order_by('media_name')
        self.fields['media_emaphsized'].choices = [(s['media_id'], s['media_name']) for s in media_qs]  
        self.fields['media_emaphsized'].initial = [s['media_id'] for s in media_qs] 
        
        #Source type choice fields. We initialize this to all values being set.
        topics_qs = topics.values('stat_topic_index', 'stat_special_topic').distinct().order_by('stat_special_topic')
        self.fields['special_topics'].choices = [(s['stat_topic_index'], s['stat_special_topic']) for s in topics_qs]  
        self.fields['special_topics'].initial = [s['stat_topic_index'] for s in topics_qs] 
        