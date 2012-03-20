''' This module includes the view functions which implement the various
search pages.
'''

# django packages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Q, Max
from django.forms import Form
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import TemplateResponseMixin, CreateView, UpdateView

# project specific packages
from forms import GeneralSearchForm, AnalyteSearchForm, AnalyteSelectForm, KeywordSearchForm, MicrobiologicalSearchForm, RegulatorySearchForm
from forms import BiologicalSearchForm, ToxicitySearchForm, PhysicalSearchForm, StatisticalSearchForm, StatisticalSourceEditForm, TabularSearchForm
from models import MethodVW, MethodSummaryVW, MethodAnalyteVW, DefinitionsDOM, AnalyteCodeRel, MethodAnalyteAllVW, MethodAnalyteJnStgVW, MethodStgSummaryVw
from models import RegQueryVW, SourceCitationRef, CitationTypeRef, RegulatoryMethodReport
from utils.forms import get_criteria, get_criteria_from_field_data, get_multi_choice
from utils.view_utils import dictfetchall, xls_response, tsv_response


def _greenness_profile(d):
    '''Returns a dicitionary with five keywords. The first keyword is profile whose is 
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
 
class FilterFormMixin(object):
    '''This mixin class is designed to be process a form where query filter conditions are set.
    The method get_qs, should check the form's cleaned data and filter the query as appropriate and
    return the query set.
    The method get_context_data, generates any context data generated from the form.
    '''
    
    form_class = Form

    def get_qs(self, form):
        return None
    
    def get_context_data(self, form):
        return {}
                                     
class SearchResultView(View, TemplateResponseMixin):
    ''' This class extends the standard view and template response mixin. This class
    should be mixed with a class that provides a get_qs(form) method, get_context_data(form) method, and a form_class parameter.
    '''
    
    result_fields = () # Fields to be displayed on the results page
    result_field_order_by = '' #Field to order the query results. If null, no order is specified
    
    header_abbrev_set = () # The header definitions to retrieve from the DOM. These should be in the order (from left to right)
    # that they will appear on the screen
    
    def get_header_defs(self):
        ''' Returns a list of DefinitionsDOM objects matching the definition_abbrev using abbrev_set. 
        The objects will only have the definition_name and definition_description field set.
        The objects will be in the same order as abbrev_set and if an object is missing or there are multiple
        in the DefinitionsDOM table, then the name in abbrev_set is used with spaces replacing underscores and words
        capitalized with a standard description.
        '''
        def_qs = DefinitionsDOM.objects.filter(definition_abbrev__in=self.header_abbrev_set)
        
        header_defs = []
        for abbrev in self.header_abbrev_set:
            try:
                header_defs.append(def_qs.get(definition_abbrev=abbrev))
            except(DefinitionsDOM.MultipleObjectsReturned, DefinitionsDOM.DoesNotExist):
                header_defs.append(DefinitionsDOM(definition_name=abbrev.replace('_', ' ').title(),
                                                  definition_description='No definition available.')) 
            
        return header_defs

    def get_values_qs(self, qs):
        ''' Returns the qs as a values query set with result_fields in the set and ordered by result_field_order_by.'''
        v_qs = qs.values(*self.result_fields).distinct()
        if self.result_field_order_by:
            v_qs = v_qs.order_by(self.result_field_order_by)
            
        return v_qs
    
    def get_results_context(self, qs):
        '''Returns a dictionary containing the query set results. By default this returns self.get_values_qs() as the 'results' key.
        If you need to process the values query set further or generate additional information from the query set, override this method.
        '''
        return {'results': self.get_values_qs(qs)}

    def get(self, request, *args, **kwargs):
        '''Process the GET request.'''
        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                context = {'search_form' : form,
                           'query_string' : '?' + request.get_full_path().split('&', 1)[1],
                           'header_defs' : self.get_header_defs(),
                           'hide_search' : True,
                           'show_results' : True}
                context.update(self.get_context_data(form))
                context.update(self.get_results_context(self.get_qs(form)))
                
                return self.render_to_response(context)          
             
            else:
                return self.render_to_response({'search_form' : form,
                                        'hide_search' : False,
                                        'show_results' : False}) 
            
        else:
            return self.render_to_response({'search_form' : self.form_class(),
                                            'hide_search' : False,
                                            'show_results' : False})
                
class ExportSearchView(View):
    ''' Extends the standard View to implement the view which exports the search results
    table. This should be extended along with the FilterFormMixin.
    '''

    export_fields = () # Fields in the query set to be exported to file
    export_field_order_by = '' # Field name to order the export query results by. If null, no order is specified
    filename = '' #Provide the name of the file to create. The appropriate suffix will be added to the filename
    
    def get_export_qs(self, qs):
        ''' Return a values list query set from the objects query set using export_fields to select fields
        and export_field_order_by to order the query set.
        '''
        export_qs = qs.values_list(*self.export_fields).distinct()
        if self.export_field_order_by:
            export_qs = export_qs.order_by(self.export_field_order_by)
            
        return export_qs
    

    def get(self, request, *args, **kwargs):
        '''Processes the get request.'''
        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                HEADINGS = [name.replace('_', ' ').title() for name in self.export_fields]
                export_type = kwargs.get('export', '')
                
                if export_type == 'tsv':
                    return tsv_response(HEADINGS, self.get_export_qs(self.get_qs(form)), self.filename)
                
                elif export_type == 'xls':
                    return xls_response(HEADINGS, self.get_export_qs(self.get_qs(form)), self.filename)
                
                else:
                    return Http404
            
            else:
                return Http404
            
        else:
            return Http404
                
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

class AnalyteSelectView(View, TemplateResponseMixin):
    ''' Extends the standard view to implement the analyte select pop up page. '''

    template_name = 'find_analyte.html'
    
    def get(self, request, *args, **kwargs):
        if request.GET:
            select_form = AnalyteSelectForm(request.GET)
            kind = request.GET.get('kind', 'name')
            
        else:
            select_form = AnalyteSelectForm(request.GET)
            kind = 'name'
            
        return self.render_to_response({'select_form' : select_form,
                                        'kind' : kind})
        

class MicrobiologicalSearchView(SearchResultView, FilterFormMixin):
    '''Extends the SearchResultView and FilterFormMixin to implement the microbiological search page.'''
    
    template_name = "microbiological_search.html"
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
            form = KeywordSearchForm(request.GET)
            if form.is_valid():
                # Execute as raw query since  it uses a CONTAINS clause and context grammer.
                cursor = connection.cursor() #@UndefinedVariable
                cursor.execute('SELECT DISTINCT score(1) method_summary_score, mf.method_id, mf.source_method_identifier method_number, \
mf.link_to_full_method, mf.mimetype, mf.revision_id, mf.method_official_name, mf.method_descriptive_name, mf.method_source \
FROM nemi_data.method_fact mf, nemi_data.revision_join rj \
WHERE mf.revision_id = rj.revision_id AND \
(CONTAINS(mf.source_method_identifier, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + form.cleaned_data['keywords'] + '.<progression> \
<seq><rewrite>transform((TOKENS, "{", "}", " "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", " ; "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "AND"))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "ACCUM"))</rewrite></seq>\
</progression></textquery><score datatype="INTEGER" algorithm="COUNT"/></query>\', 1) > 1 \
OR CONTAINS(rj.method_pdf, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + form.cleaned_data['keywords'] + '.<progression> \
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
                return self.render_to_response({'form': form,
                                                'current_url' : current_url,
                                                'results' : results}) 
                
            else:
                # There is an error in form validation so resubmit the form.
                return self.render_to_response({'form' : form})

        else:
            #Render a blank form
            form = KeywordSearchForm()
            return self.render_to_response({'form' : form})
        
class BaseMethodSummaryView(View, TemplateResponseMixin):
    '''Extends the basic view to implement a method summary page. This class
    should be extended to implement specific pages by at least providing
    a template_name parameter.
    '''    
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
                                                       
        #Get analytes for the method and each analyte's synonyms.
        analyte_data = []
        
        analyte_qs = _analyte_value_qs(self.data.method_id)
        for r in analyte_qs:
            name = r['analyte_name'].lower()
            code = r['analyte_code'].lower()
            inner_qs = AnalyteCodeRel.objects.filter(Q(analyte_name__iexact=name)|Q(analyte_code__iexact=code)).values_list('analyte_code', flat=True).distinct()
            qs = AnalyteCodeRel.objects.all().filter(analyte_code__in=inner_qs).order_by('analyte_name').values('analyte_name')
            syn = []
            for a in qs:
                syn.append(a['analyte_name'])
                
            analyte_data.append({'r' : r, 'syn' : syn})
            
        context = self.get_context(request, *args, **kwargs)
        context['data'] = self.data
        context['analyte_data'] = analyte_data
        
        return self.render_to_response(context)
    

class MethodSummaryView(BaseMethodSummaryView):   
    ''' Extends the BaseMethodSummaryView to implement the standard Method Summary page.'''

    template_name='method_summary.html'
    
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
    
class ToxicityMethodSummaryView(BaseMethodSummaryView):
    '''Extends the BaseMethodSummaryView to implement the toxicity method summary page.'''
    
    template_name = 'toxicity_method_summary.html'
    
class StreamPhysicalMethodSummaryView(DetailView):
    ''' Extends the DetailView to implement the Stream Physical Method Summary view.'''

    template_name = 'stream_physical_method_summary.html'
    context_object_name = 'data'
    model = MethodStgSummaryVw
    
class ExportMethodAnalyte(View, TemplateResponseMixin):
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
        
class AddStatisticalSourceView(CreateView):
    ''' Extends CreateView to implement the create statistiscal source page.
    '''
       
    template_name = 'create_statistic_source.html'
    form_class = StatisticalSourceEditForm
    model = SourceCitationRef
    
    def get_success_url(self):
        return reverse('search-statistical_source_detail', kwargs={'pk' : self.object.source_citation_id})        
    
    def form_valid(self, form):
        ''' Returns the success url after saving the new statistical source.
        The source is created with approve_flag set to 'F' and the code determines the new id number to use.
        '''
        self.object = form.save(commit=False)
        
        r = SourceCitationRef.objects.aggregate(Max('source_citation_id'))
        self.object.source_citation_id = r['source_citation_id__max'] + 1
        self.object.approve_flag = 'F'
        self.object.citation_type = CitationTypeRef.objects.get(citation_type='Statistic')
        self.object.insert_person = self.request.user
        
        self.object.save()
        form.save_m2m()
        
        return HttpResponseRedirect(self.get_success_url())
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddStatisticalSourceView, self).dispatch(*args, **kwargs)
    
class UpdateStatisticalSourceListView(ListView):
    ''' Extends the standard ListView to implement the view which
    will show a list of views that the logged in user can edit.
    '''
    
    template_name = 'update_stat_source_list.html'
    context_object_name = 'source_methods'
    
    def get_queryset(self):
        return SourceCitationRef.stat_methods.filter(insert_person__exact=self.request.user).order_by('source_citation')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateStatisticalSourceListView, self).dispatch(*args, **kwargs)

class UpdateStatisticalSourceView(UpdateView):
    ''' Extends the standard UpdateView to implement the Update Statistical source page.'''
    
    template_name='update_statistic_source.html'
    form_class = StatisticalSourceEditForm
    model = SourceCitationRef
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateStatisticalSourceView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('search-statistical_source_detail', kwargs={'pk' : self.object.source_citation_id})            

class StatisticSearchView(SearchResultView, FilterFormMixin):
    '''
    Extends the SearchResultView and FilterFormMixin to implement the view to display statistical methods.
    This view does not define any headers, therefore the template creates the table headers.
    '''
    
    template_name = 'statistic_search.html'
    form_class = StatisticalSearchForm
    
    def get_qs(self, form):
        qs = SourceCitationRef.stat_methods.all()
        
        if form.cleaned_data['item_type']:
            qs = qs.filter(item_type__exact=form.cleaned_data['item_type'])
            
        if form.cleaned_data['complexity'] != 'all':
            qs = qs.filter(complexity__exact=form.cleaned_data['complexity'])
            
        if form.cleaned_data['analysis_types']:
            qs = qs.filter(analysis_types__exact=form.cleaned_data['analysis_types'])
            
        if form.cleaned_data['publication_source_type']:
            qs = qs.filter(sponser_types__exact=form.cleaned_data['publication_source_type'])
            
        if form.cleaned_data['design_objectives']:
            qs = qs.filter(design_objectives__exact=form.cleaned_data['design_objectives'])
            
        if form.cleaned_data['media_emphasized']:
            qs = qs.filter(media_emphasized__exact=form.cleaned_data['media_emphasized'])
            
        if form.cleaned_data['special_topics']:
            qs = qs.filter(special_topics__exact=form.cleaned_data['special_topics'])
            
        return qs
            
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria_from_field_data(form, 'item_type'))
        criteria.append(get_criteria(form['complexity']))
        criteria.append(get_criteria_from_field_data(form, 'analysis_types'))
        criteria.append(get_criteria_from_field_data(form, 'publication_source_type'))
        criteria.append(get_criteria_from_field_data(form, 'design_objectives'))
        criteria.append(get_criteria_from_field_data(form, 'media_emphasized'))
        criteria.append(get_criteria_from_field_data(form, 'special_topics'))
        
        return {'criteria' : criteria}
        
    def get_header_defs(self):
        return None
        
    def get_results_context(self, qs):
        return {'results' : qs}
            
class StatisticalSourceSummaryView(DetailView):
    ''' Extends DetailView to implement the Statistical Source Summary view'''
    
    template_name = 'statistical_source_summary.html'
    
    model = SourceCitationRef
    
    context_object_name = 'data'
    
class StatisticalSourceDetailView(DetailView):
    ''' Extends DetailView to implement the Statistical Source Detail view.'''
    
    template_name = 'statistical_source_detail.html'
    
    model = SourceCitationRef
    
    context_object_name = 'data'
