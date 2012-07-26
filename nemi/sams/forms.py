'''
Created on Jul 25, 2012

@author: mbucknel
'''

from django.forms import Form, ModelChoiceField, ChoiceField, ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple, TextInput, Textarea

from common.models import StatisticalDesignObjective, StatisticalItemType, COMPLEXITY_CHOICES, StatisticalAnalysisType, StatisticalSourceType
from common.models import MediaNameDOM, StatisticalTopics, SourceCitationRef

class StatisticalSearchForm(Form):
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
    
class StatisticalSourceEditForm(ModelForm):
    '''Extends the ModelForm to implement the statistical source edit form.
    The verbose_help field can be retrieved in a template using the custom template filter
    'verbose_help' found in form_field_attr_filters.py.
    '''
    media_emphasized = ModelMultipleChoiceField(widget=CheckboxSelectMultiple(),
                                                queryset=MediaNameDOM.stat_media.all(),
                                                required=True,
                                                help_text="Media emphasized but not limited to")
   
    class Meta:
        model = SourceCitationRef
        fields = ('source_citation', 
                  'title', 
                  'source_organization', 
                  'country', 
                  'author',
                  'abstract_summary', 
                  'table_of_contents',
                  'publication_year', 
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
                   'design_objectives' : CheckboxSelectMultiple(),
                   'special_topics' : CheckboxSelectMultiple()}
        
        
    def __init__(self, *args, **kwargs):
        super(StatisticalSourceEditForm, self).__init__(*args, **kwargs)

        # There is a bug/feature in the MultipleChoiceField where it sets the help text for these fields to
        # a message about how to select multiple choices in a SelectMultiple widgets. Even if you change the widget
        # to CheckboxSelectMultiple, the message remains and any help_text from the model is ignored.
        # The code below sets the help for all fields that use the CheckboxSelectMultiple widget to the same help_text
        # defined in the model form. See Django bug report https://code.djangoproject.com/ticket/9321 . This may
        # be fixed in 1.4 but won't be done in 1.3.x versions.
        # For now, I'll have to duplicate the help text here.
        
        self.fields['analysis_types'].help_text = 'Do you already have the data or are you designing a monitoring program?'
        self.fields['sponser_types'].help_text = 'What type of organization produced this item?'
        self.fields['media_emphasized'].help_text = 'Water, air, biological tissue, other?'
        self.fields['design_objectives'].help_text = 'What water resources information need are you addressing, e.g., time trends, standards evaluation, etc.?'
        self.fields['special_topics'].help_text = 'Looking for help with nondetect, autocorrelation, data collected using sensor, etc.?'

        # We may want to get the verbose help from a database.
        self.fields['source_citation_name'].verbose_help = 'The published literature citation of the method, or volume from which the method comes. Ordering information is also included (if available).'