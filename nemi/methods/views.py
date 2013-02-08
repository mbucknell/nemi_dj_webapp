''' This module includes the view functions which implement the various
NEMI methods pages.
'''

# django packages

import re

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import View, ListView, TemplateView
from django.views.generic.edit import TemplateResponseMixin

# project specific packages
from common.models import DefinitionsDOM, MethodAnalyteVW, InstrumentationRef, StatisticalDesignObjective, StatisticalItemType
from common.models import StatisticalAnalysisType, StatisticalSourceType, MediaNameDOM, StatisticalTopics, Method
from common.utils.forms import get_criteria, get_multi_choice
from common.utils.view_utils import dictfetchall
from common.views import FilterFormMixin, SearchResultView, ExportSearchView, ChoiceJsonView
from forms import GeneralSearchForm, AnalyteSearchForm, MicrobiologicalSearchForm, RegulatorySearchForm
from forms import BiologicalSearchForm, ToxicitySearchForm, PhysicalSearchForm, TabularSearchForm
from models import MethodVW, MethodSummaryVW, AnalyteCodeRel, MethodAnalyteAllVW, MethodAnalyteJnStgVW, MethodStgSummaryVw, AnalyteCodeVW
from models import RegQueryVW,  RegulatoryMethodReport, RegulationRef

def _greenness_profile(d):
    '''Returns a dictionary with five keywords. The first keyword is profile whose is 
    a list of four gifs representing the greenness profile of the dictionary d or an empty list if there is not
    enough information for a complete profile. The second through 5th keyword represent the verbose greenness value for
    pbt, toxic, corrisive, and waste_amt
    '''
    def _g_value(flag):
        ''' Returns a string representing the verbose "greenness" of flag.'''
        if flag == 'N':
            return 'Green'
        elif flag == 'Y':
            return 'Not Green'
        else:
            return 'N.S.'
        
    pbt = d.get('pbt', '')
    toxic = d.get('toxic', '')
    corrosive = d.get('corrosive', '')
    waste = d.get('waste', '')
    
    g = []
    if pbt == 'N':
        g.append('ULG2.gif')
    elif pbt == 'Y':
        g.append('ULW2.gif')
        
    if toxic == 'N':
        g.append('URG2.gif')
    elif toxic == 'Y':
        g.append('URW2.gif')
        
    if corrosive == 'N':
        g.append('LLG2.gif')
    elif corrosive == 'Y':
        g.append('LLW2.gif')
        
    if waste == 'N':
        g.append('LRG2.gif')
    elif waste == 'Y':
        g.append('LRW2.gif')
        
    if len(g) != 4:
        g = []

    return {'profile' : g, 
            'pbt' : _g_value(pbt), 
            'hazardous' : _g_value(toxic),
            'corrosive' : _g_value(corrosive),
            'waste_amt' : _g_value(waste)}
    

def _analyte_value_qs(method_id):
    ''' Returns the analyte data values query set for the method_id.'''
    
    analyte_data = MethodAnalyteVW.objects.filter(preferred__exact=-1, method_id__exact=method_id).order_by('analyte_name')
    return analyte_data.values('analyte_name',
                               'analyte_code',
                               'dl_value',
                               'dl_units_description',
                               'dl_units',
                               'accuracy',
                               'accuracy_units_description',
                               'accuracy_units',
                               'precision',
                               'precision_units_description',
                               'precision_units',
                               'false_positive_value',
                               'false_negative_value',
                               'prec_acc_conc_used').distinct()
 
def _clean_name(name):
    ''' Returns name with characters removed or substituted to produce a name suitable
    to be saved as a file with an extension.
    '''
    remove_pattern = re.compile(r'<.*?>|\(|\)|#')
    replace_pattern = re.compile(r'\s|\,|/|\.')
    
    result = remove_pattern.sub('', name)
    result = replace_pattern.sub('_', result)
    
    return result


class GeneralSearchFormMixin(FilterFormMixin):
    '''Extends the FilterFormMixin to implement the search form used on the General Search page.'''

    form_class = GeneralSearchForm
    
    def get_qs(self, form):
        qs = MethodVW.objects.all()

        if form.cleaned_data['media_name'] != 'all':
            qs = qs.filter(media_name__exact=form.cleaned_data['media_name'])

        if form.cleaned_data['source'] != 'all':
            qs = qs.filter(method_source__contains=form.cleaned_data['source'])

        if form.cleaned_data['method_number'] != 'all':
            qs = qs.filter(method_id__exact=int(form.cleaned_data['method_number']))
            
        if form.cleaned_data['instrumentation'] != 'all':
            qs = qs.filter(instrumentation_id__exact=int(form.cleaned_data['instrumentation']))  
        
        if form.cleaned_data['method_subcategory'] != 'all':
            qs = qs.filter(method_subcategory_id__exact=int(form.cleaned_data['method_subcategory']))
        
        qs = qs.filter(method_type_id__in=form.cleaned_data['method_types'])
        
        return qs
        
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria(form['media_name']))
        criteria.append(get_criteria(form['source']))
        criteria.append(get_criteria(form['method_number']))
        criteria.append(get_criteria(form['instrumentation']))
        criteria.append(get_criteria(form['method_subcategory']))
        
        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}
        
        
class ExportGeneralSearchView(ExportSearchView, GeneralSearchFormMixin):
    '''Extends the ExportSearchView and GeneralSearchFormMixin to implement the
    general search export file generation.
    '''
    export_fields = ('method_id', 
                     'source_method_identifier',
                     'method_descriptive_name', 
                     'media_name', 
                     'method_source',
                     'instrumentation_description',
                     'method_subcategory',
                     'method_category',
                     'method_type_desc')
    export_field_order_by = 'source_method_identifier'
    filename = 'general_search'
               
class GeneralSearchView(GeneralSearchFormMixin, SearchResultView):
    '''Extends the SearchResultView and GeneralSearchFormMixin to implement the
    general search page.
    '''
    result_fields = ('source_method_identifier',
                     'method_source',
                     'instrumentation_description',
                     'method_descriptive_name',
                     'media_name',
                     'method_category',
                     'method_subcategory',
                     'method_type_desc',
                     'method_id',
                     'assumptions_comments',
                     'pbt',
                     'toxic',
                     'corrosive',
                     'waste')
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'MEDIA_NAME',
                         'METHOD_SOURCE',
                         'INSTRUMENTATION',
                         'METHOD_CATEGORY',
                         'METHOD_SUBCATEGORY',
                         'METHOD_TYPE',
                         'GREENNESS')
    
    template_name = 'general_search.html'
    
    def get_results_context(self, qs):
        '''Returns a list of dictionaries where each element in the list contains two keywords.
        The keyword m contains a model object in self.get_values_qs. The keyword, greenness,
        contains the greenness profile information for that object.
        '''
        return {'results' : [{'m' : r, 'greenness': _greenness_profile(r)} for r in self.get_values_qs(qs)]} 
                    
class AnalyteSearchFormMixin(FilterFormMixin):
    '''Extends the FilterFormMixin to implement the Analyte search form used on the analyte search pages.'''
    
    form_class = AnalyteSearchForm
    
    def get_qs(self, form):
        qs = MethodAnalyteAllVW.objects.all()
    
        if form.cleaned_data['analyte_kind'] == 'code':
            qs = qs.filter(analyte_code__iexact=form.cleaned_data['analyte_value'])
        else: # assume analyte kind is name
            qs = qs.filter(analyte_name__iexact=form.cleaned_data['analyte_value'])
            
        if form.cleaned_data['media_name'] != 'all':
            qs = qs.filter(media_name__exact=form.cleaned_data['media_name'])
        
        if form.cleaned_data['source'] != 'all':
            qs = qs.filter(method_source__contains=form.cleaned_data['source'])
            
        if form.cleaned_data['instrumentation'] != 'all':
            qs = qs.filter(instrumentation_id__exact=form.cleaned_data['instrumentation'])
            
        if form.cleaned_data['method_subcategory'] != 'all':
            qs = qs.filter(method_subcategory_id__exact=form.cleaned_data['method_subcategory'])

        qs = qs.filter(method_type_desc__in=form.cleaned_data['method_types'])
        return qs
        
    def get_context_data(self, form):
        criteria = []
        if form.cleaned_data['analyte_kind'] == 'code':
            criteria.append(('Analyte code', form.cleaned_data['analyte_value']))
        else:
            criteria.append(('Analyte name', form.cleaned_data['analyte_value']))
        criteria.append(get_criteria(form['media_name']))
        criteria.append(get_criteria(form['source']))
        criteria.append(get_criteria(form['instrumentation']))
        criteria.append(get_criteria(form['method_subcategory']))

        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}

class ExportAnalyteSearchView(ExportSearchView, AnalyteSearchFormMixin):
    '''Extends the ExportSearchView and AnalyteSearchFormMixin to implement the export analyte search feature.'''
    
    export_fields = ('method_id',
                     'method_descriptive_name',
                     'method_subcategory',
                     'method_category',
                     'method_source_id',
                     'method_source',
                     'source_method_identifier',
                     'analyte_name',
                     'analyte_code',
                     'media_name',
                     'instrumentation',
                     'instrumentation_description',
                     'sub_dl_value',
                     'dl_units',
                     'dl_type',
                     'dl_type_description',
                     'dl_units_description',
                     'sub_accuracy',
                     'accuracy_units',
                     'accuracy_units_description',
                     'sub_precision',
                     'precision_units',
                     'precision_units_description',
                     'false_negative_value',
                     'false_positive_value',
                     'prec_acc_conc_used',
                     'precision_descriptor_notes',
                     'relative_cost',
                     'relative_cost_symbol')
    export_field_order_by = 'method_id'
    filename = 'analyte_search'
    
class AnalyteSearchView(SearchResultView, AnalyteSearchFormMixin):
    '''Extends the SearchResultsView and AnalyteSearchFormMixin to implement the analyte search page.'''
    
    template_name = 'analyte_search.html'
    
    result_fields = ('method_source_id',
                     'method_id',
                     'source_method_identifier',
                     'method_source',
                     'method_descriptive_name',
                     'dl_value',
                     'dl_units_description',
                     'dl_type_description',
                     'dl_type',
                     'accuracy',
                     'accuracy_units_description',
                     'accuracy_units',
                     'precision',
                     'precision_units_description',
                     'precision_units',
                     'prec_acc_conc_used',
                     'dl_units',
                     'instrumentation_description',
                     'instrumentation',
                     'relative_cost',
                     'relative_cost_symbol',
                     'pbt',
                     'toxic',
                     'corrosive',
                     'waste',
                     'assumptions_comments')
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                      'METHOD_SOURCE',
                      'METHOD_DESCRIPTIVE_NAME',
                      'DL_VALUE',
                      'DL_TYPE',
                      'ACCURACY',
                      'PRECISION',
                      'PREC_ACC_CONC_USED',
                      'INSTRUMENTATION',
                      'RELATIVE_COST',
                      'GREENNESS')
    
    def get_results_context(self, qs):
        '''Returns a list of dictionaries where each element in the list contains two keywords.
        The keyword m contains a model object in self.get_values_qs. The keyword, greenness,
        contains the greenness profile information for that object.
        '''
        return {'results' : [{'m' : r, 'greenness' : _greenness_profile(r)} for r in self.get_values_qs(qs)]}

class AnalyteSelectView(View):
    ''' Extends the standard view to implement a view which returns json data containing
    a list of the matching analyte values in values_list key.
    '''
    
    def get(self, request, *args, **kwargs):
        if request.GET:
            if request.GET['selection']:
                if request.GET['kind'] == 'code':
                    qs = AnalyteCodeVW.objects.filter(
                        analyte_analyte_code__icontains=request.GET['selection']).order_by('analyte_analyte_code').values_list('analyte_analyte_code', 
                                                                                                                               flat=True).distinct()
                else:
                    qs = AnalyteCodeRel.objects.filter(analyte_name__icontains=request.GET['selection']).order_by('analyte_name').values_list('analyte_name', flat=True)                                   
                
                if qs.count() > 0:
                    qs_str = '[' + ', '.join('"%s"' % v for v in qs) + ']'
                    return HttpResponse('{"values_list" : ' +  qs_str+ "}", mimetype="application/json")
            
        return HttpResponse('{"values_list" : ""}', mimetype="application/json")
 
        
class MethodCountView(ChoiceJsonView):
    '''
    Extends the standard view to retrieve and return as a json object the total number of methods in the datastore.
    '''
    
    def get(self, request, *args, **kwargs):
        ## TODO: Check to see if MethodVW includes statistical methods.
        return HttpResponse('{"method_count" : "' + str(MethodVW.objects.count()) + '"}', mimetype="application/json");

  
class MediaNameView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the media names as a json object
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(m[0], m[0].capitalize()) for m in MethodVW.objects.values_list('media_name').distinct().order_by('media_name')]
    
class SourceView(ChoiceJsonView):
    '''
    Extends the standard view to retrieve the sources as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        
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
            
        qs = MethodVW.objects.all()
    
        sc_qs = qs.values_list('method_source', 'method_source_name').distinct().exclude(method_source__contains='EPA').exclude(method_source__contains='USGS').exclude(method_source__startswith='DOE')
        ## Need to do the next step because sc_qs is a ValuesListQuerySet and does not have an append method.
        source_choices = [(source, name) for (source, name) in sc_qs] 
        if qs.filter(method_source__contains='EPA').exists():
            source_choices.append((u'EPA', u'US Environmental Protection Agency'))
        if qs.filter(method_source__contains='USGS').exists():
            source_choices.append((u'USGS', u'US Geological Survey'))
        if qs.filter(method_source__startswith=u'DOE').exists():
            source_choices.append((u'DOE', u'US Department of Energy'))
        
        source_choices.sort(cmp=_choice_cmp)
        return source_choices
    
class InstrumentationView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the instrumentation choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        qs = MethodVW.objects.values_list('instrumentation_id', 'instrumentation_description').distinct().order_by('instrumentation_description')
        return [(str(i_id), descr) for (i_id, descr) in qs]
     
class RegulationView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the regulation choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return RegulationRef.objects.values_list('regulation', 'regulation_name').order_by('regulation_name').distinct()

class MethodTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the method type choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        qs = MethodVW.objects.all();
        if 'category' in request.GET:
            qs = qs.filter(method_category__iexact=request.GET['category'])
        qs = qs.values_list('method_type_desc').distinct().order_by('method_type_desc')
        return [(descr, descr) for (descr,) in qs]
    
class SubcategoryView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the subcategory choices as a json object.
    The subcategory choices can be filtered by specifying a get parameter, 'category'.
    '''
    def get_choices(self, request, *args, **kwargs):
        qs = MethodVW.objects.all()
        if 'category' in request.GET:
            qs = qs.filter(method_category__iexact=request.GET["category"])

        qs = qs.values_list('method_subcategory').distinct().order_by('method_subcategory')
        return [(s_descr, s_descr) for (s_descr,) in qs]
        
class GearTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the gear type choices as a json object
    '''
    def get_choices(self, request, *args, **kwargs):
        qs = InstrumentationRef.objects.filter(instrumentation_id__range=(112, 121)).order_by('instrumentation_description').values_list('instrumentation_id', 'instrumentation_description')       
        return [(str(i_id), i_descr) for (i_id, i_descr) in qs]
    
class StatObjectiveView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical design objects as a json object.
    '''
    
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_design_index), m.objective) for m in StatisticalDesignObjective.objects.exclude(objective='Revisit')]
    
class StatItemTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical item type choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_item_index), m.item) for m in StatisticalItemType.objects.all()]
class StatAnalysisTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical analysistype choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_analysis_index), m.analysis_type) for m in StatisticalAnalysisType.objects.all()]
        
class ItemTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical item type choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_item_index), m.item) for m in StatisticalItemType.objects.all()]
        
class StatSourceTypeView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical source type choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_source_index), m.source) for m in StatisticalSourceType.objects.all()]
        
class StatMediaNameView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the media name choices for statistical methodsas a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(m.media_name, m.media_name.lower().title()) for m in MediaNameDOM.stat_media.all()]
        

class StatSpecialTopicsView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the statistical special topic choices as a json object.
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(str(m.stat_topic_index), m.stat_special_topic) for m in StatisticalTopics.objects.all()]
        
    

class MicrobiologicalSearchView(SearchResultView, FilterFormMixin):
    '''Extends the SearchResultView and FilterFormMixin to implement the microbiological search page.'''
    
    template_name = 'microbiological_search.html'
    form_class = MicrobiologicalSearchForm
    
    result_fields = ('method_id',
                     'source_method_identifier',
                     'method_descriptive_name',
                     'method_source',
                     'method_source_contact',
                     'method_source_url',
                     'media_name',
                     'instrumentation_description',
                     'relative_cost_symbol',
                     'cost_effort_key')
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_SOURCE',
                         'MEDIA_NAME',
                         'GEAR_TYPE',
                         'RELATIVE_COST')
    
    def get_qs(self, form):
        qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact=5)
        
        if form.cleaned_data['analyte'] != 'all':
            qs = qs.filter(analyte_id__exact=form.cleaned_data['analyte'])
            
        qs = qs.filter(method_type_desc__in=form.cleaned_data['method_types'])
        return qs
    
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria(form['analyte']))
    
        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}
        
class BiologicalSearchView(SearchResultView, FilterFormMixin):
    '''Extends the SearchResultView and FilterFormMixin to implement the biological search page.'''
    
    template_name = 'biological_search.html'
    form_class = BiologicalSearchForm
    
    result_fields = ('method_id',
                     'source_method_identifier',
                     'method_descriptive_name',
                     'analyte_type',
                     'method_source',
                     'method_source_contact',
                     'method_source_url',
                     'method_type_desc',
                     'media_name',
                     'waterbody_type',
                     'instrumentation_description',
                     'relative_cost_symbol',
                     'cost_effort_key')
    
    header_abbrev_set = ('ANALYTE_TYPE',
                         'SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_SOURCE',
                         'METHOD_TYPE',
                         'MEDIA_NAME',
                         'WATERBODY_TYPE',
                         'GEAR_TYPE',
                         'RELATIVE_COST')
    def get_qs(self, form):
        qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id=7)
        if form.cleaned_data['analyte_type'] != 'all':
            qs = qs.filter(analyte_type__exact=form.cleaned_data['analyte_type'])
            
        if form.cleaned_data['waterbody_type'] != 'all':
            qs = qs.filter(waterbody_type__exact=form.cleaned_data['waterbody_type'])
            
        if form.cleaned_data['gear_type'] != 'all':
            qs = qs.filter(instrumentation_id__exact=form.cleaned_data['gear_type'])
        
        qs = qs.filter(method_type_desc__in=form.cleaned_data['method_types']) 
        
        return qs
    
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria(form['analyte_type']))
        criteria.append(get_criteria(form['waterbody_type']))
        criteria.append(get_criteria(form['gear_type']))
        
        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}
                  
class ToxicitySearchView(SearchResultView, FilterFormMixin):
    '''Extends the SearchResultsView and FilterFormMixin to implements the toxicity search page.'''
    
    template_name = 'toxicity_search.html'
    form_class = ToxicitySearchForm
    
    result_fields = ('method_id', 
                    'source_method_identifier',
                    'method_descriptive_name',
                    'method_subcategory',
                    'method_source',
                    'method_source_contact',
                    'method_source_url',
                    'media_name',
                    'matrix',
                    'relative_cost_symbol',
                    'cost_effort_key')
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_SUBCATEGORY',
                         'METHOD_SOURCE',
                         'MEDIA_NAME',
                         'MATRIX',
                         'RELATIVE_COST')
    
    def get_qs(self, form):
        qs = MethodAnalyteAllVW.objects.filter(method_category__exact='TOXICITY ASSAY').exclude(source_method_identifier__exact='ORNL-UDLP-01')
        
        if form.cleaned_data['subcategory'] != 'all':
            qs = qs.filter(method_subcategory__exact=form.cleaned_data['subcategory'])
            
        if form.cleaned_data['media'] != 'all':
            qs = qs.filter(media_name__exact=form.cleaned_data['media'])
            
        if form.cleaned_data['matrix'] != 'all':
            qs = qs.filter(matrix__exact=form.cleaned_data['matrix'])
            
        qs = qs.filter(method_type_desc__in=form.cleaned_data['method_types'])
        
        return qs
        
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria(form['subcategory']))
        criteria.append(get_criteria(form['media']))
        criteria.append(get_criteria(form['matrix']))
        
        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}
        
class PhysicalSearchView(SearchResultView, FilterFormMixin):
    
    template_name = 'physical_search.html'
    form_class = PhysicalSearchForm
    
    result_fields = ('method_id',
                     'source_method_identifier',
                     'method_descriptive_name',
                     'method_source',
                     'method_source_contact',
                     'method_source_url',
                     'media_name',
                     'instrumentation_description')
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_SOURCE',
                         'MEDIA_NAME',
                         'GEAR_TYPE')
    def get_qs(self, form):
        qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact=9)        
        if form.cleaned_data['analyte'] != 'all':
            qs = qs.filter(analyte_id__exact=form.cleaned_data['analyte'])

        qs = qs.filter(method_type_desc__in=form.cleaned_data['method_types']) 
        
        return qs
    
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria(form['analyte']))
        
        return {'criteria' : criteria,
                'selected_method_types' : get_multi_choice(form, 'method_types')}
            
    
class StreamPhysicalSearchView(SearchResultView):
    ''' Extends the SearchResultsView to implement the stream physical search page which has no user controlled filtering.
    '''
    
    template_name="stream_physical_search.html"
    
    result_fields = ('method_id',
                     'source_method_identifier',
                     'method_descriptive_name',
                     'method_source',
                     'method_source_contact',
                     'method_source_url',
                     'media_name',
                     'relative_cost_symbol',
                     'cost_effort_key')
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                       'METHOD_DESCRIPTIVE_NAME',
                       'METHOD_SOURCE',
                       'MEDIA_NAME',
                       'RELATIVE_COST'
                       )
    
    qs = MethodAnalyteJnStgVW.objects.filter(source_method_identifier__startswith='WRIR')

    def get(self, request, *args, **kwargs):
        context = self.get_results_context(self.qs)
        context['header_defs'] = self.get_header_defs()
        context['show_results'] = True
        return self.render_to_response(context) 
        
class RegulatorySearchFormMixin(FilterFormMixin):
    ''' Extends the FilterFormMixin to implement the query filtering part of the Regulatory Search page.
    '''
    
    form_class = RegulatorySearchForm
    
    def get_qs(self, form):
        qs = RegQueryVW.objects.exclude(method_subcategory__in=['SAMPLE/PREPARATION', 'GENERAL'])
        
        if form.cleaned_data['analyte_kind'] == 'code':
            qs = qs.filter(analyte_code__iexact=form.cleaned_data['analyte_value'])
        else:
            qs = qs.filter(analyte_name__iexact=form.cleaned_data['analyte_value'])
            
        if form.cleaned_data['regulation'] != 'all':
            qs = qs.filter(regulation__exact=form.cleaned_data['regulation'])
            
        return qs
            
    def get_context_data(self, form):
        # Retrieve analyte synonyms for display
        if form.cleaned_data ['analyte_kind'] == 'code':
            analyte_code = form.cleaned_data['analyte_value']
            analyte_qs = AnalyteCodeRel.objects.filter(analyte_code__iexact=analyte_code)
            if len(analyte_qs) == 0:
                analyte_name = None
            else:
                try:
                    analyte_name = analyte_qs.filter(preferred__exact=-1)[0].analyte_name
                except:
                    analyte_name = analyte_qs[0].analyte_name
        else:
            analyte_name = form.cleaned_data['analyte_value']
            try:
                analyte_code = AnalyteCodeRel.objects.filter(analyte_name__iexact=analyte_name)[0].analyte_code
                analyte_qs = AnalyteCodeRel.objects.filter(analyte_code__iexact=analyte_code)
            except:
                analyte_code = None
                analyte_qs = None
        if analyte_qs:    
            syn = analyte_qs.values_list('analyte_name', flat=True)
        else:
            syn = []
            
        criteria = []
        criteria.append(get_criteria(form['regulation']))
                                
        return {'criteria' : criteria,
                'analyte_name' : analyte_name,
                'analyte_code' : analyte_code,
                'syn' : syn}
    
class ExportRegulatorySearchView(ExportSearchView, RegulatorySearchFormMixin):
    '''Extends the ExportSearchView and RegulatorySearchFormMixin to implement the
    view which will export the table data.
    '''
    
    export_fields = ('method_id',
                     'method_source',
                     'method_source_id',
                     'revision_id',
                     'analyte_revision_id',
                     'source_method_identifier',
                     'regulation',
                     'regulation_name',
                     'revision_information',
                     'method_descriptive_name',
                     'method_subcategory',
                     'method_category',
                     'media_name',
                     'relative_cost_symbol',
                     'instrumentation',
                     'instrumentation_description',
                     'analyte_name',
                     'analyte_code',
                     'sub_dl_value',
                     'dl_units',
                     'dl_type',
                     'dl_type_description',
                     'dl_units_description',
                     'sub_accuracy',
                     'accuracy_units',
                     'sub_precision',
                     'precision_units',
                     'precision_units_description',
                     'false_negative_value',
                     'false_positive_value',
                     'prec_acc_conc_used',
                     'precision_descriptor_notes',
                     'link_to_full_method')
    export_field_order_by = 'method_id'
    filename = 'regulatory_search'
    
class RegulatorySearchView(SearchResultView, RegulatorySearchFormMixin):
    ''' Extends the SearchResultsView and RegulatorySearchFormMixin to implement
    the regulatory search page.
    '''
    
    template_name = 'regulatory_search.html'
    
    result_fields = ('method_source_id',
                     'regulation_name',
                     'regulation',
                     'reg_location',
                     'source_method_identifier',
                     'revision_information',
                     'revision_id',
                     'analyte_revision_id',
                     'method_source',
                     'method_descriptive_name',
                     'link_to_full_method',
                     'mimetype',
                     'method_id',
                     'dl_value',
                     'dl_units_description',
                     'dl_units',
                     'dl_type_description',
                     'dl_type',
                     'instrumentation_description',
                     'instrumentation',
                     'relative_cost',
                     'relative_cost_symbol')
    result_field_order_by = 'source_method_identifier'
    
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'REGULATION',
                         'REGULATION_LOCATION',
                         'METHOD_SOURCE',
                         'REVISION_INFO',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_DOWNLOAD',
                         'DL_VALUE',
                         'DL_TYPE',
                         'INSTRUMENTATION',
                         'RELATIVE_COST',
                         )
    
    def get_results_context(self, qs):
        results = self.get_values_qs(qs)
        
        # Need to provide a count of unique methods in the results query.
        method_count = 0
        last_method = None
        for r in results:
            if last_method != r['source_method_identifier']:
                method_count += 1
                last_method = r['source_method_identifier']
        
        return {'results' : results,
                'method_count' : method_count}
        
class TabularRegulatorySearchView(SearchResultView, FilterFormMixin):
    ''' Extends the SearchResultsForm and FilterFormMixin to implement the Tabular
    Regulatory Search page. 
    We do not provide and header definitions so the template must create the table headers.
    '''
    
    template_name = 'tabular_reg_search.html'
    form_class = TabularSearchForm
    
    result_fields = ('analyte_name',
                     'epa',
                     'standard_methods',
                     'astm',
                     'usgs',
                     'other',
                     'epa_rev_id',
                     'standard_methods_rev_id',
                     'usgs_rev_id',
                     'astm_rev_id',
                     'other_rev_id')
    
    def get_qs(self, form):
        qs = RegulatoryMethodReport.objects.all()
        if form.cleaned_data['analyte'] != 'all':
            qs = qs.filter(analyte_name__exact=form.cleaned_data['analyte'])
            
        return qs
    
    def get_results_context(self, qs):
        '''Add analyte synonyms to each result by retrieving analyte code from AnalyteCodeRel
        and generating the list of synonyms that the analyte name/code pair.
        '''
        r_context = {'results': []}
        
        v_qs = self.get_values_qs(qs)
        for r in v_qs:
            try:
                a_qs = AnalyteCodeRel.objects.filter(analyte_name__iexact=r['analyte_name'])
                analyte_code = a_qs[0].analyte_code
            except:
                analyte_code = None
                
            if analyte_code:
                syn = AnalyteCodeRel.objects.filter(analyte_code__iexact=analyte_code).values_list('analyte_name', flat=True)
            else:
                syn = []
            
            r_context['results'].append({'r' : r, 'analyte_code' : analyte_code, 'syn' : syn})
            
        return r_context
    
class ResultsView(View, TemplateResponseMixin):
    '''Extends the standard View to implement the results page.
    '''
    
    template_name = 'results.html'
    
    def get(self, request, *args, **kwargs):
        #Determine search kind
        if 'method_number' in request.GET:
            data = MethodVW.objects.filter(source_method_identifier__contains=request.GET.get('method_number'))
           
        else:
            if 'analyte_name' in request.GET or 'analyte_code' in request.GET:
                data = MethodAnalyteAllVW.objects.all()
                if request.GET.get('subcategory'):
                    data = data.filter(method_subcategory__iexact=request.GET.get('subcategory'))
                elif request.GET['category']:
                    data = data.filter(method_category__iexact=request.GET.get('category'))
                    
                if request.GET.get('analyte_name'):
                    data =  data.filter(analyte_name__iexact=request.GET.get('analyte_name')) 
                else:
                    data = data.filter(analyte_code__iexact=request.GET.get('analyte_value'))
    
            elif 'category' in request.GET:
                category = request.GET.get('category')
                if category == 'statistical':
                    ## statistical is very different from others so process separately.
                    data = Method.stat_methods.all();
                    item_type = request.GET.get('item_type', 'all')
                    complexity = request.GET.get('complexity', 'all')
                    analysis_type = request.GET.get('analysis_type', 'all')
                    publication_source_type = request.GET.get('publication_source_type', 'all')
                    study_objective = request.GET.get('study_objective', 'all')
                    media_emphasized = request.GET.get('media_emphasized', 'all')
                    special_topic = request.GET.get('special_topic', 'all')
                    
                    if item_type != 'all':
                        data = data.filter(source_citation__item_type__exact=item_type)
                    if complexity != 'all':
                        data = data.filter(sam_complexity__exact=complexity)
                    if analysis_type != 'all':
                        data = data.filter(statanalysisrel__analysis_type__exact=analysis_type)
                    if publication_source_type != 'all':
                        data = data.filter(source_citation__publicationsourcerel__source__exact=publication_source_type)
                    if study_objective != 'all':
                        data = data.filter(statdesignrel__design_objective__exact=study_objective)
                    if media_emphasized != 'all':   
                        data = data.filter(statmediarel__media_name__exact=media_emphasized)
                    if special_topic != 'all':
                        data = data.filter(stattopicrel__topic__exact=special_topic)
                    
                elif category == 'biological' and request.GET.get('subcategory', '') == 'population/community':
                    data = MethodAnalyteVW.objects.filter(method_category__iexact=category).filter(method_subcategory__iexact='population/community')
                    analyte_type = request.GET.get('analyte_type', 'all')
                    waterbody_type = request.GET.get('waterbody_type', 'all')
                    gear_type = request.GET.get('gear_type', 'all')

                    if analyte_type != 'all':
                        data = data.filter(analyte_type__exact=analyte_type)                        
                    if waterbody_type != 'all':
                        data = data.filter(waterbody_type__exact=waterbody_type)   
                    if gear_type != 'all':
                        data = data.filter(instrumentation_id__exact=gear_type)
                        
                else:   
                    data = MethodVW.objects.filter(method_category__iexact=category);                        
                    if 'subcategory' in request.GET:
                        data = data.filter(method_subcategory__in=request.GET.getlist('subcategory'))
                    else:
                        return self.render_to_response({'data' : []});
                    
                    matrix = request.GET.get('matrix', 'all')
                    if matrix != 'all':
                        data = data.filter(matrix__exact=matrix)
            
            else:
                data = MethodVW.objects.all()
            
            # Add limit by parameters if specified.
            media_name = request.GET.get('media_name', 'all')
            source = request.GET.get('source', 'all')
            instrumentation = request.GET.get('instrumentation', 'all')
            if media_name != 'all':
                data = data.filter(media_name__exact=media_name)
            if source != 'all':
                data = data.filter(method_source__contains=source)
            if instrumentation != 'all':
                data = data.filter(instrumentation_id__exact=instrumentation)
                
            if 'method_type' in request.GET:
                data = data.filter(method_type_desc__in=request.GET.getlist('method_type'))
            
        length = 'data length is ' + str(len(data))
        return self.render_to_response({"data" : data})            
                   
class KeywordSearchView(View, TemplateResponseMixin):
    '''Extends the standard View to implement the keyword search view. This form only
    processes get requests.
    '''  
    
    template_name = "keyword_search.html"
    
    def get(self, request, *args, **kwargs):
        '''Returns the http response for the keyword search form. If the form is bound
        validate the form and the execute a raw SQL query to return matching methods. The resulting 
        query set will be shown using pagination and in score order.
        '''
        if request.GET:
            # Form has been submitted.
            keyword = request.GET['keyword_search_field']
            if keyword.strip() == '':
                #Render a blank form
                return self.render_to_response({'error' : True})
            
            else:
                # Execute as raw query since  it uses a CONTAINS clause and context grammer.
                cursor = connection.cursor() #@UndefinedVariable
                cursor.execute('SELECT DISTINCT score(1) method_summary_score, mf.method_id, mf.source_method_identifier method_number, \
mf.link_to_full_method, mf.mimetype, mf.revision_id, mf.method_official_name, mf.method_descriptive_name, mf.method_source \
FROM nemi_data.method_fact mf, nemi_data.revision_join rj \
WHERE mf.revision_id = rj.revision_id AND \
(CONTAINS(mf.source_method_identifier, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + keyword + '.<progression> \
<seq><rewrite>transform((TOKENS, "{", "}", " "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", " ; "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "AND"))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "ACCUM"))</rewrite></seq>\
</progression></textquery><score datatype="INTEGER" algorithm="COUNT"/></query>\', 1) > 1 \
OR CONTAINS(rj.method_pdf, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + keyword + '.<progression> \
<seq><rewrite>transform((TOKENS, "{", "}", " "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", " ; "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "AND"))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "ACCUM"))</rewrite></seq>\
</progression></textquery><score datatype="INTEGER" algorithm="COUNT"/></query>\', 2) > 1) \
ORDER BY score(1) desc;')
                results_list = dictfetchall(cursor)
                paginator = Paginator(results_list, 20)
                
                try:
                    page = int(request.GET.get('page', '1'))
                except ValueError:
                    page = 1
    
                # If page request is out of range, deliver last page of results.
                try:
                    results = paginator.page(page)
                except (EmptyPage, InvalidPage):
                    results = paginator.page(paginator.num_pages)
    
                path = request.get_full_path()
                # Remove the &page parameter.
                current_url = path.rsplit('&page=')[0]
                return self.render_to_response({'keyword': keyword,
                                                'current_url' : current_url,
                                                'results' : results})
            
        else:
            #Render a blank form
            return self.render_to_response({})
        
class BrowseMethodsView(ListView):
    '''
    Extends ListView to implement the browse all methods page. Methods are sorted by category, subcategory, 
    and identifier.
    '''
    template_name = 'browse_methods.html'
    
    queryset = MethodVW.objects.order_by('method_category', 'method_subcategory', 'source_method_identifier')
    
        
class BaseMethodSummaryView(View, TemplateResponseMixin):
    '''Extends the basic view to implement a method summary page. This class
    should be extended to implement specific pages by at least providing
    a template_name parameter.
    '''    
    # The set of fields for which we want definitions in the view
    field_abbrev_set = []
   
    def get_field_defs(self):
        defs = DefinitionsDOM.objects.filter(definition_abbrev__in=self.field_abbrev_set)
        field_defs = {}
        
        for d in defs:
            field_defs[d.definition_abbrev] = {'name': d.definition_name, 
                                               'description' : d.definition_description,
                                              }
            
        return field_defs;
        
    def get_context(self, request, *args, **kwargs):
        '''Returns additional context information to be sent to the template'''
        return {}
    
    def get_summary_data(self, **kwargs):
        '''Returns the summary data object which must contain a method_id.
        By default the MethodSummaryVW is used and the method_id is passed
        as a kwargs argument.
        '''
        if 'method_id' in kwargs:
            try:
                return MethodSummaryVW.objects.get(method_id=kwargs['method_id'])
            except MethodSummaryVW.DoesNotExist:
                return None
        else:
            raise Http404
        
    def get_analyte_data(self, summary_data):
        ''' Return a list of analytes information for the method object in summary data. 
        By default this returns a list of dictionaries containing information about each
        analyte in the method. Each dictionary contains two keywords.
        'r' keyword contains one analyte values query set object for the method id. The 'syn'
        keyword contains the a list of synonyms for that analyte.
        '''
        analyte_data = []
        
        analyte_qs = _analyte_value_qs(summary_data.method_id)
        for r in analyte_qs:
            name = r['analyte_name'].lower()
            code = r['analyte_code'].lower()
            inner_qs = AnalyteCodeRel.objects.filter(Q(analyte_name__iexact=name)|Q(analyte_code__iexact=code)).values_list('analyte_code', flat=True).distinct()
            qs = AnalyteCodeRel.objects.all().filter(analyte_code__in=inner_qs).order_by('analyte_name').values('analyte_name')
            syn = []
            for a in qs:
                syn.append(a['analyte_name'])
                
            analyte_data.append({'r' : r, 'syn' : syn})  
            
        return analyte_data
          
    def get(self, request, *args, **kwargs):
        '''Processes the get request and returns the appropriate http response.
        The method summary information for a method id is retrieved from MethodSummaryVW
        using the method_id passed as a keyword argument. The method's analytes are
        retrieved along with each analyte's synonymns.
        '''
        self.data = self.get_summary_data(**kwargs)
        if self.data == None:
            return self.render_to_response ({'data' : None,
                                             'analyte_data' : None}) 
                                                       
        context = self.get_context(request, *args, **kwargs)
        context['field_defs'] = self.get_field_defs()
        context['data'] = self.data
        context['analyte_data'] = self.get_analyte_data(self.data)
        
        return self.render_to_response(context)
    
    
class MethodSummaryView(BaseMethodSummaryView):   
    ''' Extends the BaseMethodSummaryView to implement the standard Method Summary page.'''

    template_name='method_summary.html'
    
    field_abbrev_set = ['MEDIA_NAME',
                        'METHOD_SUBCATEGORY',
                        'METHOD_SOURCE',
                        'CITATION',
                        'BRIEF_METHOD_SUMMARY',
                        'SCOPE_AND_APPLICATION',
                        'APPLICABLE_CONC_RANGE',
                        'METHOD_DOWNLOAD',
                        'INTERFERENCES',
                        'QC_REQUIREMENTS',
                        'SAMPLE_HANDLING',
                        'MAX_HOLDING_TIME',
                        'RELATIVE_COST',
                        'SAMPLE_PREP_METHODS'
                       ]
    
    def get_context(self, request, *args, **kwargs):
        '''Returns a dictionary with one keyword, 'notes' which contains a value query set generated from MethodAnalyteVw which
        contains the two fields, precision_descriptor_notes and dl_note for the method_id.
        '''
        notes = MethodAnalyteVW.objects.filter(method_id__exact=self.data.method_id).values('precision_descriptor_notes', 'dl_note').distinct()
        return {'notes' : notes}

class RegulatoryMethodSummaryView(MethodSummaryView):
    '''Extends the MethodSummaryView but overrides get_summary_data to use revision_id and the RegQueryVw table.
    '''

    def get_summary_data(self, **kwargs):
        if 'rev_id' in kwargs:
            qs = RegQueryVW.objects.filter(revision_id__exact=kwargs['rev_id'])
            if len(qs) == 0:
                return None
            else:
                return qs[0]
            
        else:
            raise Http404
            
class BiologicalMethodSummaryView(BaseMethodSummaryView):
    '''Extends the BaseMethodSummaryView to implement the biological method summary page.'''
    
    template_name = 'biological_method_summary.html'

    field_abbrev_set = ['MEDIA_NAME',
                        'METHOD_SUBCATEGORY',
                        'TARGET_ORGANISM',
                        'METHOD_SOURCE',
                        'CITATION',
                        'BRIEF_METHOD_SUMMARY',
                        'SCOPE_AND_APPLICATION',
                        'METHOD_DOWNLOAD',
                        'INTERFERENCES',
                        'QC_REQUIREMENTS',
                        'SAMPLE_HANDLING',
                        'MAX_HOLDING_TIME',
                        'RELATIVE_COST',
                        'SAMPLE_PREP_METHODS'
                       ]
    
        
class ToxicityMethodSummaryView(BaseMethodSummaryView):
    '''Extends the BaseMethodSummaryView to implement the toxicity method summary page.'''
    
    template_name = 'toxicity_method_summary.html'

    field_abbrev_set = [
                        'METHOD_SOURCE',
                        'CITATION',
                        'BRIEF_METHOD_SUMMARY',
                        'SCOPE_AND_APPLICATION',
                        'APPLICABLE_CONC_RANGE',
                        'METHOD_DOWNLOAD',
                        'INTERFERENCES',
                        'QC_REQUIREMENTS',
                        'SAMPLE_HANDLING',
                        'MAX_HOLDING_TIME',
                        'RELATIVE_COST',
                        'ENDPOINT',
                       ] 
    
       
class StreamPhysicalMethodSummaryView(BaseMethodSummaryView):
    ''' Extends the BaseMethodSummaryView to implement the Stream Physical Method Summary view.
    Overrides get_summary_data to get method from MethodStgSummaryVw. Overrides get_analyte_data since
    this view does not require analyte data.
    '''

    template_name = 'stream_physical_method_summary.html'
    
    field_abbrev_set = ['MEDIA_NAME',
                        'METHOD_SOURCE',
                        'CITATION',
                        'BRIEF_METHOD_SUMMARY',
                        'SCOPE_AND_APPLICATION',
                        'INTERFERENCES',
                        'QC_REQUIREMENTS',
                        'RELATIVE_COST',
                       ]    
    
    def get_summary_data(self, **kwargs):
        if 'method_id' in kwargs:
            try:
                return MethodStgSummaryVw.objects.get(method_id=kwargs['method_id'])
            except MethodStgSummaryVw.DoesNotExist:
                return None
        else:
            raise Http404
        
    def get_analyte_data(self, summary_data):
        return []
    
    
class ExportMethodAnalyte(View):
    ''' Extends the standard view. This view creates a
    tab-separated file of the analyte data. Required keyword argument,
    method_id is used to retrieve the analyte information. This uses
    the same query that is used in the MethodSummaryView to retrieve
    the analyte data.
    '''

    def get(self, request, *args, **kwargs):
        '''Processes the get request. The data to export is retrieved from the analyte value
        queryset. A tab separated values file is created.
        '''
        if 'method_id' in kwargs:
            HEADINGS = ('Analyte',
                        'Detection Level',
                        'Bias',
                        'Precision',
                        'Pct False Positive',
                        'Pct False Negative',
                        'Spiking Level')
            qs = _analyte_value_qs(kwargs['method_id'])
        
            response = HttpResponse(mimetype='text/tab-separated-values')
            response['Content-Disposition'] = 'attachment; filename=%s_analytes.tsv' % kwargs['method_id']
            
            response.write('\t'.join(HEADINGS))
            response.write('\n')
            
            for row in qs:
                response.write('%s\t' % row['analyte_name'])
                
                if row['dl_value'] == 999:
                    response.write('N/A\t')
                else:
                    response.write('%.2f %s\t' %(row['dl_value'], row['dl_units']))
                    
                if row['accuracy'] == -999:
                    response.write('N/A\t')
                else:
                    response.write('%d %s\t' %(row['accuracy'], row['accuracy_units']))
                    
                if row['precision'] == 999:
                    response.write('N/A\t')
                else:
                    response.write('%.2f %s\t' %(row['precision'], row['precision_units']))
                    
                if row['false_positive_value'] == None:
                    response.write('\t')
                    
                else:
                    response.write('%s\t' % row['false_positive_value'])
                    
                if row['false_negative_value'] == None:
                    response.write('\t')
                else:
                    response.write('%s\t' % row['false_negative_value'])
                    
                    
                if row['prec_acc_conc_used']:
                    response.write('%.2f %s\t' %(row['prec_acc_conc_used'], row['dl_units']))
                else:
                    response.write('\t')

                response.write('\n')
            
            return response
        

class MethodPdfView(View):
    ''' Extends the standard View to serve a method's pdf file if it it exists in the database.
    '''
    
    def get(self, request, *args, **kwargs):        
        cursor = connection.cursor()
        cursor.execute('SELECT mimetype, method_pdf, source_method_identifier from nemi_data.method_summary_vw where method_id=%s',
                       [kwargs['method_id']])
        results_list = dictfetchall(cursor)

        if results_list:
            if results_list[0]['MIMETYPE'] and results_list[0]['METHOD_PDF']:
                response = HttpResponse(mimetype=results_list[0]['MIMETYPE'])
                response['Content-Disposition'] = 'attachment;filename=%s.pdf' % _clean_name(results_list[0]['SOURCE_METHOD_IDENTIFIER'])
        
                pdf = results_list[0]['METHOD_PDF'].read()
                response.write(pdf)
            
                return response
            
            else:
                return HttpResponse('No pdf stored for method %s' % results_list[0]['SOURCE_METHOD_IDENTIFIER'])
        
        else:
            raise Http404
        
