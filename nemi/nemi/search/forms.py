''' This module contains the forms needed to implement the NEMI search pages '''

from django.forms import Form, ModelForm, ChoiceField, MultipleChoiceField, CheckboxSelectMultiple, RadioSelect, CharField, SelectMultiple, TextInput, HiddenInput
from django.forms import IntegerField, Textarea
from django.utils.safestring import mark_safe
from models import *
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

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
    method_types = CheckBoxMultipleChoiceField()
        
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
    method_types = CheckBoxMultipleChoiceField()    
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
    method_types = CheckBoxMultipleChoiceField()
    
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
    method_types = CheckBoxMultipleChoiceField()

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
        
class PhysicalSearchForm(Form):
    
    analyte = ChoiceField()
    method_types = CheckBoxMultipleChoiceField()
    def __init__(self, *args, **kwargs):
        super(PhysicalSearchForm, self).__init__(*args, **kwargs)
        
        #Get analytes
        qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact='9').values_list('analyte_name', 'analyte_code', 'analyte_id').distinct().order_by('analyte_name', 'analyte_code')
        self.fields['analyte'].choices = [(u'all', u'Any')] + [(a_id, '%s (%s)' %(name, code)) for (name, code, a_id) in qs]
        
        #Get method types
        qs = MethodVW.objects.filter(method_subcategory_id__exact='9').values_list('method_type_desc', flat=True).distinct().order_by('method_type_desc')
        self.fields['method_types'].choices = [(m, m) for m in qs]
        self.fields['method_types'].initial = [m for m in qs]
        
        
class StatisticalSearchForm(Form):
    
    item_type = ModelChoiceField(queryset=StatisticalItemType.objects.all(), empty_label='Any', required=False)
    complexity = ChoiceField(choices=[(u'all', u'Any')] + COMPLEXITY_CHOICES, required=False)
    analysis_types = ModelChoiceField(queryset=StatisticalAnalysisType.objects.all(), empty_label='Any', required=False)
    sponser_types = ModelChoiceField(queryset=StatisticalSourceType.objects.all(), empty_label='Any', required=False)
    design_objectives = ModelChoiceField(queryset=StatisticalDesignObjective.objects.all(), empty_label='Any', required=False)
    media_emphasized = ModelChoiceField(queryset=MediaNameDOM.objects.all(), empty_label='Any', required=False)
    special_topics = ModelChoiceField(queryset=StatisticalTopics.objects.all(), empty_label='Any', required=False)
    
class AddStatisticalSourceForm(ModelForm):
        
    class Meta:
        model = SourceCitationRef
        fields = ('insert_person_name', 
                  'source_citation', 
                  'title', 
                  'source_organization', 
                  'country', 
                  'author',
                  'publication_year', 
                  'abstract_summary', 
                  'source_citation_name',
                  'link',
                  'notes',
                  'item_type', 
                  'item_type_note',
                  'sponser_types',
                  'sponser_type_note',
                  'analysis_types',
                  'design_objectives',
                  'complexity',
                  'level_of_training',
                  'media_emphasized',
                  'media_emphasized_note',
                  'subcategory',
                  'special_topics')
        
        widgets = {'source_citation' : TextInput(attrs={'size' : 30}),
                   'source_citation_name' : Textarea(attrs={'rows' : 9, 'cols' : 50}),
                   'insert_person_name' : TextInput(attrs={'size' : 25}),
                   'title' : Textarea(attrs={'rows' : 3, 'cols' : 50}),
                   'author' : Textarea(attrs={'rows' : 3, 'cols' : 50}),
                   'abstract_summary' : Textarea(attrs={'rows' : 10, 'cols' : 50}),
                   'table_of_contents' : Textarea(attrs={'rows' : 10, 'cols': 50}),
                   'link' : TextInput(attrs={'size' : 50}),
                   'notes' : Textarea(attrs={'rows' : 9, 'cols' : 50}),
                   'publication_year' : TextInput(attrs={'size' : 4}),
                   'country' : TextInput(attrs={'size' : 50}),
                   'item_type_note' : TextInput(attrs={'size' : 50}),
                   'sponser_type_note' : TextInput(attrs={'size' : 50}),
                   'media_emphasized_note' : TextInput(attrs={'size' : 50}),
                   'subcategory' : TextInput(attrs={'size' : 50}),
                   'analysis_types' : CheckboxSelectMultiple(),
                   'sponser_types' : CheckboxSelectMultiple(),
                   'media_emphasized' : CheckboxSelectMultiple(),
                   'design_objectives' : CheckboxSelectMultiple(),
                   'special_topics' : CheckboxSelectMultiple()}
        
class StatisticSearchFormSecondTry(Form):
    item_type = ChoiceField(choices= [
        (u'all', u'Any'),
        (u'1', u'Report / Guidance Document'),
        (u'2', u'Journal Article'),
        (u'3', u'Book'),
        (u'4', u'Book Chapter / Section'),
        (u'5', u'Downloadable Software'),
        (u'6', u'Online Calculator'),
        (u'7', u'Other')]
    )
    complexity = ChoiceField(choices= [
        (u'all', u'Any'),
        (13, u'Low'),
        (14, u'Medium'),
        (15, u'High')]
    )
    analysis_type = ChoiceField(choices= [
        (u'all', u'Any'),
        (u'1', u'Monitoring program design'),
        (u'2', u'Analysis of exsisting data'),
        (u'3', u'Both')  ]                          
                                
    )
    sponsor_type = MultipleChoiceField(
        choices= [
            (u'1', u'Journal'),
            (u'2', u'Non-governmental Organization'),
            (u'3', u'Government Agency (Federal, USA)'),
            (u'4', u'Government Agency (State, USA)'),
            (u'5', u'Government Agency (Tribal, NA)'),
            (u'6', u'Academic Institution'),
            (u'7', u'Regional Organization'),
            (u'8', u'Other'),
            (u'9', u'International Government Agency'),
            (u'10', u'Industry')],
        widget=CheckboxSelectMultiple(), 
        required=False
    )
    design_objective = MultipleChoiceField(
        choices= [
            (u'1', u'Summarize data in terms of means, medians, distributions, percentiles'),
            (u'2', u'Evaluate compliance with a threshold value'),
            (u'3', u'Characterize temporal trends (long-term, annual, seasonal)'),
            (u'4', u'Characterize  spatial trends'),
            (u'5', u'Design or evaluate data from a probability survey'),
            (u'6', u'Evaluate relationships among variables'),
            (u'7', u'Estimate river flow statistics'),
            (u'8', u'Estimate downstream loadings of chemicals or suspended materials'),
            (u'9', u'Develop source identification/apportionment information'),
            (u'10', u'Determine flow-adjusted chemical concentrations'),
            (u'11', u'Derive water quality threshold values'),
            (u'12', u'Estimate volumes of contaminated soil, sediment, or other material'),
            (u'13', u'Compare a location to a reference site'),
            (u'14', u'Compare control and experimental treatments'),
            (u'15', u'Evaluate "continuous" data (e.g., measurements collected hourly or more often)'),
            (u'16', u'Evaluate biological data (e.g., benthic macroinvertebrates, fish, diatoms)'),
            (u'17', u'Evaluate bioassay/bioaccumulation/toxicity data'),
            (u'18', u'Estimate concentrations at unsampled locations') ],                 
        widget=CheckboxSelectMultiple(), 
        required=False
    )
    media_emaphsized = MultipleChoiceField(
        choices= [
            (u'1', u'Water'),
            (u'2', u'Agricultural Products'),
            (u'3', u'Air'),
            (u'4', u'Animal Tissue'),
            (u'5', u'Soil / Sediment'),
            (u'6', u'Various'),
            (u'7', u'Other'),
            (u'8', u'Surface Water'),
            (u'9', u'Ground Water'),
            (u'10', u'Sediment'),
            (u'11', u'Dredged Material'),
            (u'12', u'Biological')],
        widget=CheckboxSelectMultiple(), 
        required=False
    )
    special_topics = MultipleChoiceField(
        choices= [
            (u'1', u'Handling non-detects'),
            (u'2', u'Identifying outliers'),
            (u'3', u'Evaluating whether data follows a certain (e.g. normal) distribution'),
            (u'4', u'Assessing and managing autocorrlation'),
            (u'5', u'Measurements taken using a water quality sensor'),
            (u'6', u'Characterizing the uncertainty of an estimate')],                                              
        widget=CheckboxSelectMultiple(), 
        required=False
    )
    