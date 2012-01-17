''' This module includes the view functions which implement the various
search pages.
'''

# standard python packages
import types

# django packages
from django.db import connection
from django.db.models import Q
from django.forms import Form
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import View, DetailView
from django.views.generic.edit import TemplateResponseMixin

# Provides conversion to Excel format
from xlwt import Workbook

# project specific packages
from forms import *
from models import MethodVW, MethodSummaryVW, MethodAnalyteVW, DefinitionsDOM, AnalyteCodeRel, MethodAnalyteAllVW, MethodAnalyteJnStgVW, MethodStgSummaryVw
from models import sourceCitationRef,statisticalDesignObjective,statisticalItemType,relativeCostRef,statisticalSourceType, MediaNameDOM, statisticalTopics, statisticalAnalysisType

def _choice_select(field):
    '''Returns the visible choice from the form field variable. The function
    assumes choice values are integer or string
    '''
    if type(field.field.choices[1][0]) is types.IntType:
        return dict(field.field.choices).get(int(field.data))
    return dict(field.field.choices).get(field.data)

def _dictfetchall(cursor):
    '''Returns all rows from the cursor query as a dictionary with the key value equal to column name in uppercase'''
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]
               
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
    
def _tsv_response(headings, vl_qs):
    ''' Returns an http response which contains a tab-separate-values file
    representing the values list query set, vl_qs, and using headings as the 
    column headers.
    '''
    response = HttpResponse(mimetype='text/tab-separated-values')
    response['Content-Disposition'] = 'attachment; filename=general_search.tsv'

    response.write('\t'.join(headings))
    response.write('\n')

    for row in vl_qs:
        for col in row:
            response.write('%s\t' % str(col))
        response.write('\n')

    return response

def _xls_response(headings, vl_qs):
    '''Returns an http response which contains an Excel file
    representing the values list query set, vl_qs, and using headings
    as the column headers.
    '''
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=general_search.xls'
    
    wb = Workbook()
    ws = wb.add_sheet('sheet 1')
    
    for col_i in range(len(headings)):
        ws.write(0, col_i, headings[col_i])
    
    for row_i in range(len(vl_qs)):
        for col_i in range(len(vl_qs[row_i])):
            ws.write(row_i + 1, col_i, vl_qs[row_i][col_i])
    
    wb.save(response)
    
    return response

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

class SearchFormMixin(object):
    '''This mixin implements the form processing part of a search view page.
    The form parameter is set to the form class used to implement the search form.
    The method get_query_and_context_from_form extracts the query set represented by the valid form. Any
    additional context information is generated from the form is created as part of this method.
    '''

    form = Form #Search form which generates the result query set, qs, and context
   
    def get_query_and_context_from_form(self):
        '''Generate the query set that is a derived from the form along with any additional context
        data that is required from the form.
        '''
        self.qs = None
        self.context = {}
        
class SearchResultView(View, TemplateResponseMixin):
    ''' This class extends the standard view and template response mixin. The class should be extended along with
    the SearchFormMixin to implement the search pages.
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

    def get_values_qs(self):
        ''' Returns the qs as a values query set with result_fields in the set and ordered by result_field_order_by.'''
        v_qs = self.qs.values(*self.result_fields).distinct()
        if self.result_field_order_by:
            v_qs = v_qs.order_by(self.result_field_order_by)
            
        return v_qs
    
    def get_results_context(self):
        '''Returns the results context variable. By default this returns self.get_values_qs().
        If you need to process the values query set further, override this method.
        '''
        return self.get_values_qs()

    def get_valid_form_response(self, request, *args, **kwargs):
        '''Returns the http response when the form generated from request is valid.'''
        self.context.update({'search_form' : self.search_form,
                             'header_defs' : self.get_header_defs(),
                             'results' : self.get_results_context(),
                             'query_string' : '?' + request.get_full_path().split('&', 1)[1],
                             'hide_search' : True,
                             'show_results' : True})
        return self.render_to_response(self.context)
     
    def get_invalid_form_response(self, request, *args, **kwargs):
        '''Returns the http response when the form generated from request is invalid.'''
        return self.render_to_response({'search_form' : self.search_form,
                                        'hide_search' : False,
                                        'show_results' : False}) 
          
    def get_empty_form_response(self, request, *args, **kwargs):
        '''Return the http response when the request does not contain any get data.'''
        return self.render_to_response({'search_form' : self.form(),
                                        'hide_search' : False,
                                        'show_results' : False})

    def get(self, request, *args, **kwargs):
        '''Process the GET request.'''
        if request.GET:
            self.search_form = self.form(request.GET)
            if self.search_form.is_valid():
                self.get_query_and_context_from_form()
                return self.get_valid_form_response(request, *args, **kwargs)
             
            else:
                return self.get_invalid_form_response(request, *args, **kwargs)   
            
        else:
            return self.get_empty_form_response(request, *args, **kwargs)
                
class ExportSearchView(View):
    ''' This class extends the standard View to implement the view which exports the search results
    table. This should be extended along with the SearchFormMixin.
    '''

    export_fields = () # Fields in the query set to be exported to file
    export_field_order_by = '' # Field name to order the export query results by. If null, no order is specified
    
    def get_export_qs(self):
        ''' Return a values list query set from the objects query set using export_fields to select fields
        and export_field_order_by to order the query set.
        '''
        export_qs = self.qs.values_list(*self.export_fields).distinct()
        if self.export_field_order_by:
            export_qs = export_qs.order_by(self.export_field_order_by)
            
        return export_qs
    
    def get_valid_form_response(self, request, *args, **kwargs):
        ''' Returns the http response when request contains a valid form. The kind of
         file to export is specified in the keyword argument 'export'. This method
         handles 'tsv' (tab separated files) and 'xls' (Excel files) keywords.
         '''
        HEADINGS = [name.replace('_', ' ').title() for name in self.export_fields]
        export_type = kwargs.get('export', '')
        
        if export_type == 'tsv':
            return _tsv_response(HEADINGS, self.get_export_qs())
        
        elif export_type == 'xls':
            return _xls_response(HEADINGS, self.get_export_qs())
        
        else:
            return Http404

    def get_invalid_form_response(self, request, *args, **kwargs):
        '''Returns the http response when request contains an invalid form.'''
        return Http404
    
    def get_empty_form_response(self, request, *args, **kwargs):
        '''Returns the http response when request does not contain get data.'''
        return Http404
    
    def get(self, request, *args, **kwargs):
        '''Processes the get request.'''
        if request.GET:
            self.search_form = self.form(request.GET)
            if self.search_form.is_valid():
                self.get_query_and_context_from_form()
                return self.get_valid_form_response(request, *args, **kwargs)
            
            else:
                return self.get_invalid_form_response(request, *args, **kwargs)
            
        else:
            return self.get_empty_form_response(request, *args, **kwargs)
                
class GeneralSearchFormMixin(SearchFormMixin):
    '''Extends the SearchFormMixin to implement the search form used on the General Search page.'''

    form = GeneralSearchForm

    def get_query_and_context_from_form(self):
        '''Overrides the parent method. The query set is generated from the MethodVW model and is filtered
        by the contents of the form. Also generate two context dictionary values, criteria and selected_method_types
        from the search form.
        '''       
        self.context = {}
        self.qs = MethodVW.objects.all()
        criteria = []
        
        if self.search_form.cleaned_data['media_name'] != 'all':
            self.qs = self.qs.filter(media_name__exact=self.search_form.cleaned_data['media_name'])
            criteria.append((self.search_form['media_name'].label, _choice_select(self.search_form['media_name'])))
        
        if self.search_form.cleaned_data['source'] != 'all':
            self.qs = self.qs.filter(method_source__contains=self.search_form.cleaned_data['source'])
            criteria.append((self.search_form['source'].label, _choice_select(self.search_form['source'])))
                            
        if self.search_form.cleaned_data['method_number'] != 'all':
            self.qs = self.qs.filter(method_id__exact=int(self.search_form.cleaned_data['method_number']))
            criteria.append((self.search_form['method_number'].label, _choice_select(self.search_form['method_number'])))
            
        if self.search_form.cleaned_data['instrumentation'] != 'all':
            self.qs = self.qs.filter(instrumentation_id__exact=int(self.search_form.cleaned_data['instrumentation']))  
            criteria.append((self.search_form['instrumentation'].label, _choice_select(self.search_form['instrumentation'])))
        
        if self.search_form.cleaned_data['method_subcategory'] != 'all':
            self.qs = self.qs.filter(method_subcategory_id__exact=int(self.search_form.cleaned_data['method_subcategory']))
            criteria.append((self.search_form['method_subcategory'].label, _choice_select(self.search_form['method_subcategory'])))
            
        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(int(k)) for k in self.search_form.cleaned_data['method_types']]
        
        self.qs = self.qs.filter(method_type_id__in=self.search_form.cleaned_data['method_types']) 
        
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types
        
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
    
    def get_results_context(self):
        '''Returns a list of dictionaries where each element in the list contains two keywords.
        The keyword m contains a model object in self.get_values_qs. The keyword, greenness,
        contains the greenness profile information for that object.
        '''
        return [{'m' : r, 'greenness': _greenness_profile(r)} for r in self.get_values_qs()] 
                    
class AnalyteSearchFormMixin(SearchFormMixin):
    '''Extends the SearchFormMixin to implement the Analyte search form used on the analyte search pages.'''
    
    form = AnalyteSearchForm
    
    def get_query_and_context_from_form(self):
        '''Overrides the generic method. The query set is generated from the MethodAnalyteAllVW model and is filtered
        by the contents of the form. Also generate two context dictionary values, criteria and selected_method_types
        from the search form.
        '''
        self.context = {}
        self.qs = MethodAnalyteAllVW.objects.all()
        criteria = []

        if self.search_form.cleaned_data['analyte_kind'] == 'code':
            self.qs = self.qs.filter(analyte_code__iexact=self.search_form.cleaned_data['analyte_value'])
            criteria.append(('Analyte code', self.search_form.cleaned_data['analyte_value']))
        else: # assume analyte kind is name
            self.qs = self.qs.filter(analyte_name__iexact=self.search_form.cleaned_data['analyte_value'])
            criteria.append(('Analyte name', self.search_form.cleaned_data['analyte_value']))
            
        if self.search_form.cleaned_data['media_name'] != 'all':
            self.qs = self.qs.filter(media_name__exact=self.search_form.cleaned_data['media_name'])
            criteria.append((self.search_form['media_name'].label, _choice_select(self.search_form['media_name'])))
        
        if self.search_form.cleaned_data['source'] != 'all':
            self.qs = self.qs.filter(method_source__contains=self.search_form.cleaned_data['source'])
            criteria.append((self.search_form['source'].label, _choice_select(self.search_form['source'])))
            
        if self.search_form.cleaned_data['instrumentation'] != 'all':
            self.qs = self.qs.filter(instrumentation_id__exact=self.search_form.cleaned_data['instrumentation'])
            criteria.append((self.search_form['instrumentation'].label, _choice_select(self.search_form['instrumentation'])))
            
        if self.search_form.cleaned_data['method_subcategory'] != 'all':
            self.qs = self.qs.filter(method_subcategory_id__exact=self.search_form.cleaned_data['method_subcategory'])
            criteria.append((self.search_form['method_subcategory'].label, _choice_select(self.search_form['method_subcategory'])))

        self.qs = self.qs.filter(method_type_desc__in=self.search_form.cleaned_data['method_types'])
        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(k) for k in self.search_form.cleaned_data['method_types']]
            
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types      

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
    
    def get_results_context(self):
        '''Returns a list of dictionaries where each element in the list contains two keywords.
        The keyword m contains a model object in self.get_values_qs. The keyword, greenness,
        contains the greenness profile information for that object.
        '''
        return [{'m' : r, 'greenness' : _greenness_profile(r)} for r in self.get_values_qs()] 

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
        

class MicrobiologicalSearchView(SearchResultView, SearchFormMixin):
    '''Extends the SearchResultView and SearchFormMixin to implement the microbiological search page.'''
    
    template_name = "microbiological_search.html"
    form = MicrobiologicalSearchForm
    
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
    
    def get_query_and_context_from_form(self):
        '''Overrides the generic method. The query set is generated from the MethodAnalyteAllVW model and is filtered
        by the contents of the form. Also generates two context dictionary values, criteria and selected_method_types
        from the search form.
        '''
        self.context = {}
        criteria = []
        self.qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact=5)
        
        if self.search_form.cleaned_data['analyte'] != 'all':
            self.qs = self.qs.filter(analyte_id__exact=self.search_form.cleaned_data['analyte'])
            criteria.append((self.search_form['analyte'].label, _choice_select(self.search_form['analyte'])))
            
        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(k) for k in self.search_form.cleaned_data['method_types']]
        
        self.qs = self.qs.filter(method_type_desc__in=self.search_form.cleaned_data['method_types']) 
        
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types
        
class BiologicalSearchView(SearchResultView, SearchFormMixin):
    '''Extends the SearchResultView and SearchFormMixin to implement the biological search page.'''
    
    template_name = 'biological_search.html'
    form = BiologicalSearchForm
    
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
    
    def get_query_and_context_from_form(self):
        '''Overrides the generic method. The query set is generated from the MethodAnalyteAllVW model and is filtered
        by the contents of the form. Also generate two context dictionary values, criteria and selected_method_types
        from the search form.
        '''
        self.context = {}
        criteria = []
        
        self.qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id=7)
        if self.search_form.cleaned_data['analyte_type'] != 'all':
            self.qs = self.qs.filter(analyte_type__exact=self.search_form.cleaned_data['analyte_type'])
            criteria.append((self.search_form['analyte_type'].label, _choice_select(self.search_form['analyte_type'])))
            
        if self.search_form.cleaned_data['waterbody_type'] != 'all':
            self.qs = self.qs.filter(waterbody_type__exact=self.search_form.cleaned_data['waterbody_type'])
            criteria.append((self.search_form['waterbody_type'].label, _choice_select(self.search_form['waterbody_type'])))
            
        if self.search_form.cleaned_data['gear_type'] != 'all':
            self.qs = self.qs.filter(instrumentation_id__exact=self.search_form.cleaned_data['gear_type'])
            criteria.append((self.search_form['gear_type'].label, _choice_select(self.search_form['gear_type'])))

        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(k) for k in self.search_form.cleaned_data['method_types']]
        
        self.qs = self.qs.filter(method_type_desc__in=self.search_form.cleaned_data['method_types']) 
        
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types
        
class ToxicitySearchView(SearchResultView, SearchFormMixin):
    '''Extends the SearchResultsView and SearchFormMixin to implements the toxicity search page.'''
    
    template_name = 'toxicity_search.html'
    form = ToxicitySearchForm
    
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
    
    def get_query_and_context_from_form(self):
        '''Overrides the generic method. The query set is generated from the MethodAnalyteAllVW model and is 
        filter by the contents of the form. Also generates two context dictionary values, criteria and selected_method_types
        form the search_form.
        '''
        self.context = {}
        criteria = []
        self.qs = MethodAnalyteAllVW.objects.filter(method_category__exact='TOXICITY ASSAY').exclude(source_method_identifier__exact='ORNL-UDLP-01')
        
        if self.search_form.cleaned_data['subcategory'] != 'all':
            self.qs = self.qs.filter(method_subcategory__exact=self.search_form.cleaned_data['subcategory'])
            criteria.append((self.search_form['subcategory'].label, _choice_select(self.search_form['subcategory'])))
            
        if self.search_form.cleaned_data['media'] != 'all':
            self.qs = self.qs.filter(media_name__exact=self.search_form.cleaned_data['media'])
            criteria.append((self.search_form['media'].label, _choice_select(self.search_form['media'])))
            
        if self.search_form.cleaned_data['matrix'] != 'all':
            self.qs = self.qs.filter(matrix__exact=self.search_form.cleaned_data['matrix'])
            criteria.append((self.search_form['matrix'].label, _choice_select(self.search_form['matrix'])))
            
        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(k) for k in self.search_form.cleaned_data['method_types']]
        
        self.qs = self.qs.filter(method_type_desc__in=self.search_form.cleaned_data['method_types']) 
        
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types
        
class PhysicalSearchView(SearchResultView, SearchFormMixin):
    
    template_name = 'physical_search.html'
    form = PhysicalSearchForm
    
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
    
    def get_query_and_context_from_form(self):
        self.context = {}
        criteria = []
        
        self.qs = MethodAnalyteAllVW.objects.filter(method_subcategory_id__exact=9)
        
        if self.search_form.cleaned_data['analyte'] != 'all':
            self.qs = self.qs.filter(analyte_id__exact=self.search_form.cleaned_data['analyte'])
            criteria.append((self.search_form['analyte'].label, _choice_select(self.search_form['analyte'])))

        method_type_dict = dict(self.search_form['method_types'].field.choices)
        if len(self.search_form.cleaned_data['method_types']) == len(method_type_dict):
            selected_method_types = []
        else:
            selected_method_types = [method_type_dict.get(k) for k in self.search_form.cleaned_data['method_types']]
        self.qs = self.qs.filter(method_type_desc__in=self.search_form.cleaned_data['method_types']) 
        
        self.context['criteria'] = criteria
        self.context['selected_method_types'] = selected_method_types
    
class StreamPhysicalSearchView(SearchResultView, TemplateResponseMixin):
    
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
        return self.render_to_response({'header_defs' : self.get_header_defs(),
                                'results' : self.get_results_context(),
                                'show_results' : True})                

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
                results_list = _dictfetchall(cursor)
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
        
    def get(self, request, *args, **kwargs):
        '''Processes the get request and returns the appropriate http response.
        The method summary information for a method id is retrieved from MethodSummaryVW
        using the method_id passed as a keyword argument. The method's analytes are
        retrieved along with each analyte's synonymns.
        '''
        if 'method_id' in kwargs:
            try: 
                data = MethodSummaryVW.objects.get(method_id=kwargs['method_id'])
            except MethodSummaryVW.DoesNotExist:
                data = None
                
            #Get analytes for the method and each analyte's synonyms.
            analyte_data = []
            
            analyte_qs = _analyte_value_qs(kwargs['method_id'])
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
            context['data'] = data
            context['analyte_data'] = analyte_data
            return self.render_to_response(context)
    
        else:
            raise Http404

class MethodSummaryView(BaseMethodSummaryView):   
    ''' Extends the BaseMethodSummaryView to implement the standard Method Summary page.'''

    template_name='method_summary.html'
    
    def get_context(self, request, *args, **kwargs):
        '''Returns a dictionary with one keyword, 'notes' which contains a value query set generated from MethodAnalyteVw which
        contains the two fields, precision_descriptor_notes and dl_note for the method_id.
        '''
        notes = MethodAnalyteVW.objects.filter(method_id__exact=kwargs['method_id']).values('precision_descriptor_notes', 'dl_note').distinct()
        return {'notes' : notes}

    
class BiologicalMethodSummaryView(BaseMethodSummaryView):
    '''Extends the BaseMethodSummaryView to implement the biological method summary page.'''
    
    template_name = 'biological_method_summary.html'
    
class ToxicityMethodSummaryView(BaseMethodSummaryView):
    '''Extends the BaseMethodSummaryView to implement the toxicity method summary page.'''
    
    template_name = 'toxicity_method_summary.html'
    
class StreamPhysicalMethodSummaryView(DetailView):

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
        
class StatisticSearchView(SearchResultView, TemplateResponseMixin):
    
    template_name = 'statistic_search.html'
    
#    '''Extends the SearchView to implement the Statistical Method Search Page. '''
    
    header_abbrev_set = ('TITLE',
                         'SOURCE_ORGANIZATION',
                         'COUNTRY',
                         'AUTHOR',
                         'ABSTRACT_SUMMARY',
                         'TABLE_OF_CONTENTS',
                         'SOURCE_CITATION',
                         'LINK',
                         'NOTES')   
    
    form = StatisticSearchForm
    
    def get_query_and_context_from_form(self):
        '''Returns the http response for the keyword search form. If the form is bound
        validate the form and the execute a raw SQL query to return matching methods. The resulting 
        query set will be shown using pagination and in score order.
        '''
        self.context = {}
        self.qs = sourceCitationRef.objects.all()
        criteria = []
#
############################################################################################################
## Nothing here is being used....
#        # Execute as raw query since. 
#        cursor = connection.cursor() #@UndefinedVariable
#        cursor.execute("SELECT DISTINCT \
#a.title, \
#a.source_organization, \
#a.country, \
#a.author, \
#a.abstract_summary, \
#a.table_of_contents, \
#a.source_citation, \
#a.link, \
#a.notes \
#FROM \
#source_citation_ref a, \
#stat_design_rel b, \
#stat_media_rel c, \
#stat_source_rel d, \
#stat_topics_rel e, \
#statistical_analysis_type f, \
#statistical_design_objective g, \
#statistical_item_type h, \
#statistical_topics i, \
#statistical_source_type j \
#WHERE \
#a.source_citation_id = b.source_citation_id \
#AND a.source_citation_id = c.source_citation_id \
#AND a.source_citation_id = d.source_citation_id \
#AND a.source_citation_id = e.source_citation_id \
#AND a.analysis_type = f.stat_analysis_index \
#AND b.stat_design_index = g.stat_design_index \
#AND a.item_type = h.stat_item_index \
#AND e.stat_topics_index = i.stat_topic_index;")
#        results = _dictfetchall(cursor)
#        self
#################################################################################################################
            
            
class StatisticSearchViewSecondTry(View,TemplateResponseMixin):
            
    template_name = 'statistic_search_2ndTry.html'
            
    def get(self, request, *args, **kwargs):
        '''Returns the http response for the keyword search form. If the form is bound
        validate the form and the execute a raw SQL query to return matching methods. The resulting 
        query set will be shown using pagination and in score order.
        '''
        if request.GET:
            # Form has been submitted.
            form = StatisticSearchFormSecondTry(request.GET)
            if form.is_valid():
                cursor = connection.cursor() #@UndefinedVariable
                cursor.execute("SELECT DISTINCT \
a.title, \
a.source_organization, \
a.country, \
a.author, \
a.abstract_summary, \
a.table_of_contents, \
a.source_citation, \
a.link, \
a.notes \
FROM \
source_citation_ref a, \
stat_design_rel b, \
stat_media_rel c, \
stat_source_rel d, \
stat_topics_rel e, \
statistical_analysis_type f, \
statistical_design_objective g, \
statistical_item_type h, \
statistical_topics i, \
statistical_source_type j \
WHERE \
a.source_citation_id = b.source_citation_id \
AND a.source_citation_id = c.source_citation_id \
AND a.source_citation_id = d.source_citation_id \
AND a.source_citation_id = e.source_citation_id \
AND a.analysis_type = f.stat_analysis_index \
AND b.stat_design_index = g.stat_design_index \
AND a.item_type = h.stat_item_index \
AND e.stat_topics_index = i.stat_topic_index;")
                results_list = _dictfetchall(cursor)   
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
            form = StatisticSearchFormSecondTry()
            return self.render_to_response({'form' : form})

