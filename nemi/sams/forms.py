'''
Created on Jul 25, 2012

@author: mbucknel
'''

from django.forms import Form, ModelChoiceField, ChoiceField, ModelMultipleChoiceField, CheckboxSelectMultiple, TextInput, Textarea
from django.forms import CharField, IntegerField, URLField

from common.forms import BaseDefinitionsForm
from common.models import StatisticalDesignObjective, StatisticalItemType, COMPLEXITY_CHOICES, LEVEL_OF_TRAINING_CHOICES, StatisticalAnalysisType, StatisticalSourceType
from common.models import MediaNameDOM, StatisticalTopics, MethodSourceRef, StatAnalysisRelStg, StatDesignRelStg, StatTopicRelStg, StatMediaRelStg

class SAMSSearchForm(Form):
    '''Extends the standard form to implement the query filtering form for the Statistical Methods'''
    
    study_objective = ModelChoiceField(queryset=StatisticalDesignObjective.objects.exclude(objective='Revisit'),
                                       label='What are you interested in',
                                       empty_label='Any', 
                                       required=False,
                                       help_text='What water resources information need are you addressing, e.g., time trends, standards, evaluation, etc?')
    item_type = ModelChoiceField(queryset=StatisticalItemType.objects.all(), 
                                 empty_label='Any', 
                                 required=False, 
                                 help_text='The form of the item, e.g., book, journal article, web site, etc.')
    complexity = ChoiceField(choices=[(u'all', u'Any')] + COMPLEXITY_CHOICES, 
                             required=False,
                             help_text='Relatively speaking...')
    analysis_type = ModelChoiceField(queryset=StatisticalAnalysisType.objects.all(), 
                                     empty_label='Any', 
                                     required=False,
                                     help_text='Do you already have the data or are you designing a monitoring program?')
    publication_source_type = ModelChoiceField(queryset=StatisticalSourceType.objects.all(), 
                                               empty_label='Any', 
                                               required=False,
                                               help_text='What type of organization produced this item?')
    media_emphasized = ModelChoiceField(queryset=MediaNameDOM.stat_media.all(), 
                                        empty_label='Any', 
                                        required=False,
                                        help_text='Water, air, biological tissue, other?')
    special_topic = ModelChoiceField(queryset=StatisticalTopics.objects.all(), 
                                     empty_label='Any', 
                                     required=False,
                                     help_text='Looking for help with nondetects, autocorrelation, data collected using sensors, etc?')
    
class StatMethodEditForm(BaseDefinitionsForm):
    source_method_identifier = CharField(max_length=30,
                                         widget=TextInput(attrs={'size' : 30}))
    method_official_name = CharField(max_length=250,
                                     widget=Textarea(attrs={'rows' : 3, 'cols' : 50}))
    method_source = ModelChoiceField(queryset=MethodSourceRef.objects.all())
    country = CharField(max_length=100, 
                        required=False)
    author = CharField(max_length=450, 
                       widget=Textarea(attrs={'rows': 3, 'cols' : 50}))
    brief_method_summary = CharField(max_length=4000, 
                                     widget=Textarea(attrs={'rows' : 10, 'cols' : 50}))
    table_of_contents = CharField(max_length=1000, 
                                  required=False, 
                                  widget=Textarea(attrs={'rows': 10, 'cols' : 50}))
    publication_year = IntegerField(max_value=9999, 
                                    min_value=0,
                                    widget=TextInput(attrs={'size': 4}))
    source_citation_name = CharField(max_length=450, 
                                     widget=Textarea(attrs={'rows' : 9, 'cols' : 50}))
    link_to_full_method = URLField(max_length=240, 
                                   required=False,
                                   widget=TextInput(attrs={'size' : 50}))
    assumptions_comments = CharField(max_length=2000, 
                         required=False, 
                         widget=Textarea(attrs={'rows' : 9, 'cols' : 50}))
    item_type = ModelChoiceField(queryset=StatisticalItemType.objects.all())
    item_type_note = CharField(max_length=50, 
                               required=False,
                               widget=TextInput(attrs={'size' : 50}))
    sponser_types = ModelMultipleChoiceField(queryset=StatisticalSourceType.objects.all(), 
                                             widget=CheckboxSelectMultiple)
    sponser_type_note = CharField(max_length=50, 
                                  required=False,
                                  widget=TextInput(attrs={'size': 50}))
    analysis_types = ModelMultipleChoiceField(queryset=StatisticalAnalysisType.objects.all(), 
                                              widget=CheckboxSelectMultiple)
    design_objectives = ModelMultipleChoiceField(queryset=StatisticalDesignObjective.objects.all(), 
                                                 widget=CheckboxSelectMultiple)
    sam_complexity = ChoiceField(choices=[('', '-------')] + COMPLEXITY_CHOICES)
    level_of_training = ChoiceField(choices=[('' ,'--------')] + LEVEL_OF_TRAINING_CHOICES)
    media_emphasized = ModelMultipleChoiceField(queryset=MediaNameDOM.stat_media.all(),
                                                widget=CheckboxSelectMultiple)
    media_emphasized_note = CharField(max_length=50, 
                                      required=False,
                                      widget=TextInput(attrs={'size' : 50}))
    media_subcategory = CharField(max_length=150, 
                                  required=False,
                                  widget=TextInput(attrs={'size' : 50}))
    special_topics = ModelMultipleChoiceField(queryset=StatisticalTopics.objects.all(), 
                                              required=False,
                                              widget=CheckboxSelectMultiple)
        
    def get_source_citation_object(self, obj):
        ''' Returns obj with the SourceCitationRef fields filled in from the form's cleaned data
        This method assumes that the form has been validated and that cleaned_data attribute is available and
        obj should be a SourceCitationRef object.
        '''
        data = self.cleaned_data
        obj.source_citation = data['source_method_identifier']
        obj.title = data['method_official_name']
        obj.country = data['country']
        obj.author = data['author']
        obj.table_of_contents = data['table_of_contents']
        obj.publication_year = data['publication_year']
        obj.source_citation_name = data['source_citation_name']
        obj.link = data['link_to_full_method']
        obj.item_type = data['item_type']
        obj.item_type_note = data['item_type_note']
        obj.sponser_type_note = data['sponser_type_note']
        
        return obj
        
    def get_method_object(self, obj):
        ''' Returns obj with the MethodAbstract fields filled in from the form's cleaned data.
        This method assumes that the form has been validated and that the cleaned data attribute is available and
        that object is a descendant of MethodAbstract.
        '''
        data = self.cleaned_data
        
        obj.method_source = data['method_source']
        obj.source_method_identifier = data['source_method_identifier']
        obj.method_descriptive_name = data['source_citation_name']
        obj.method_official_name = data['method_official_name']
        obj.brief_method_summary = data['brief_method_summary']
        obj.link_to_full_method = data['link_to_full_method']
        obj.assumptions_comments = data['assumptions_comments']
        obj.sam_complexity = data['sam_complexity']
        obj.level_of_training = data['level_of_training']
        obj.media_emphasized_note = data['media_emphasized_note']
        obj.media_subcategory = data['media_subcategory']
        
        return obj
    
    def get_analysis_types(self, method_id):
        result = [StatAnalysisRelStg(method_id=method_id, analysis_type=t) for t in self.cleaned_data['analysis_types']]
        return result
        
    def get_design_objectives(self, method_id):
        result = [StatDesignRelStg(method_id=method_id, design_objective=t) for t in self.cleaned_data['design_objectives']]
        return result
    
    def get_media_emphasized(self, method_id):
        result = [StatMediaRelStg(method_id=method_id, media_name=t) for t in self.cleaned_data['media_emphasized']]
        return result
    
    def get_special_topics(self, method_id):
        result = [StatTopicRelStg(method_id=method_id, topic=t) for t in self.cleaned_data['special_topics']]
        return result
    