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
from django.views.generic import View
from django.views.generic.edit import TemplateResponseMixin

# Provides conversion to Excel format
from xlwt import Workbook

# project specific packages
from forms import GeneralSearchForm, AnalyteSearchForm, AnalyteSelectForm, KeywordSearchForm, MicrobiologicalSearchForm
from models import MethodVW, MethodSummaryVW, MethodAnalyteVW, DefinitionsDOM, AnalyteCodeRel, MethodAnalyteAllVW

def _choice_select(field):
    '''Return the visible choice from the form field variable. The function
    assumes choice values are integer or string
    '''
    if type(field.field.choices[1][0]) is types.IntType:
        return dict(field.field.choices).get(int(field.data))
    return dict(field.field.choices).get(field.data)

def _dictfetchall(cursor):
    '''Return all rows from the cursor query as a dictionary with the key value equal to column name in uppercase'''
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]
    
def _get_header_defs(abbrev_set):
    '''Return a list of DefinitionsDOM objects matching the definition_abbrev using abbrev_set. 
    The objects will only have the definition_name and definition_description field set.
    The objects will be in the same order as abbrev_set and if an object is mssing or there are multiple
    in the DefinitionsDOM table, then the name in abbrev_set is used with spaces replacing underscores and words
    capitialized with a standard description.
    '''
    def_qs = DefinitionsDOM.objects.filter(definition_abbrev__in=abbrev_set)
    header_defs = []
    for abbrev in abbrev_set:
        try:
            header_defs.append(def_qs.get(definition_abbrev=abbrev))
        except(DefinitionsDOM.MultipleObjectsReturned, DefinitionsDOM.DoesNotExist):
            header_defs.append(DefinitionsDOM(definition_name=abbrev.replace('_', ' ').title(),
                                              definition_description='No definition available.')) 
            
    return header_defs
               
def _greenness_profile(d):
    '''Return a dicitionary with five keywords. The first keyword is profile whose is 
    a list of four gifs representing the greenness profile of the dictionary d or an empty list if there is not
    enough information for a complete profile. The second through 5th keyword represent the verbose greenness value for
    pbt, toxic, corrisive, and waste_amt
    '''
    def _g_value(flag):
        ''' Return a string representing the verbose "greenness" of flag.'''
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
    ''' Return an http response which contains a tab-separate-values file
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
    '''Return an http response which contains an Excel file
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

class BaseSearchView(View):

    form = Form #Search form which generates the result query set, qs, and context
   
    def get_query_and_context_from_form(self):
        '''Generate the query set that is a derived from the form along with any additional context
        data that is required from the form and put in self.qs.
        This function assumes that the form has been validated.
        Any additional information that is derived from the search form should be
        put in self.context.
        '''
        self.qs = None
        self.context = {}
        
    def get_valid_form_response(self, request, *args, **kwargs):
        return HttpResponse("Default response")
    
    def get_invalid_form_response(self, request, *args, **kwargs):
        return HttpResponse("Invalid form")
    
    def get_empty_form_response(self, request, *args, **kwargs):
        return HttpResponse("Empty form")
    
    def get(self, request, *args, **kwargs):
        if request.GET:
            self.search_form = self.form(request.GET)
            if self.search_form.is_valid():
                self.get_query_and_context_from_form()
                return self.get_valid_form_response(request, *args, **kwargs)
             
            else:
                return self.get_invalid_form_response(request, *args, **kwargs)   
            
        else:
            return self.get_empty_form_response(request, *args, **kwargs)
        
class SearchResultMixin(object):
    ''' Class is used to generate the context to be used to generate a results page'''
    
    result_fields = () # Fields to be displayed on the results page
    result_field_order_by = '' #Field to order the query results. If null, no order is specified
    
    header_abbrev_set = () # The header definitions to retrieve from the DOM. These should be in the order (from left to right)
    # that they will appear on the screen
    
    def get_values_qs(self, qs):
        ''' Return the qs as a values query set with result_fields in the set and ordered by result_field_order_by.
        '''
        v_qs = qs.values(*self.result_fields).distinct()
        if self.result_field_order_by:
            v_qs = v_qs.order_by(self.result_field_order_by)
            
        return v_qs
    
    def get_results_context(self, qs):
        return self.get_values_qs(qs)

    def get_valid_context(self, request, form, qs):
        return  {'search_form' : form,
                'results' : self.get_results_context(qs),
                'query_string' : '?' + request.get_full_path().split('&', 1)[1],
                'hide_search' : True,
                'show_results' : True,
                'header_defs' : _get_header_defs(self.header_abbrev_set)}
        
    def get_invalid_context(self, request, form):
        return {'search_form' : form,
                'hide_search' : False,
                'show_results' : False}
        
class ExportSearchMixin(object):

    export_fields = () # Fields in the query set to be exported to file
    export_field_order_by = '' # Field name to order the export query results by. If null, no order is specified
    
    def get_base_queryset(self):
        return self.qs
    
    def http_response(self, export_type):
        HEADINGS = [name.replace('_', '').title() for name in self.export_fields]
        
        export_qs = self.get_base_queryset().values_list(*self.export_fields).distinct()
        if self.export_field_order_by:
            export_qs = export_qs.order_by(self.export_field_order_by)
            
        if export_type == 'tsv':
            return _tsv_response(HEADINGS, export_qs)
        
        elif export_type == 'xls':
            return _xls_response(HEADINGS, export_qs)
         
        else:
            return Http404
        
class BaseGeneralSearchView(BaseSearchView):

    form = GeneralSearchForm

    def get_query_and_context_from_form(self):
        '''Overrides the generic method. The query set is generated from the MethodVW model and is filtered
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
        
class ExportGeneralSearchView(BaseGeneralSearchView, ExportSearchMixin):
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
           
    def get_valid_form_response(self, request, *args, **kwargs):
        return self.http_response(kwargs.get('export', '')) 

    def get_invalid_form_response(self, request, *args, **kwargs):
        return Http404
    
class GeneralSearchView(BaseGeneralSearchView, SearchResultMixin, TemplateResponseMixin):
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
        r_qs = super(GeneralSearchView, self).get_results_context(qs)
        return [{'m' : r, 'greenness': _greenness_profile(r)} for r in r_qs] 
    
    def get_valid_form_response(self, request, *args, **kwargs):
        self.context.update(self.get_valid_context(request, self.search_form, self.qs))
        return self.render_to_response(self.context)
    
    def get_invalid_form_response(self, request, *args, **kwargs):
        return self.render_to_response(self.get_invalid_context(request, self.search_form))
    
    def get_empty_form_response(self, request, *args, **kwargs):
        return self.render_to_response(self.get_invalid_context(request, self.form()))
    

class MethodSummaryView(View, TemplateResponseMixin):
    
    ''' Extends the standard view. This view only processes GET requests. The
    keyword argument method_id is used to retrieve the MethodSummaryVW and MethodAnalyteVW information
    '''

    template_name="method_summary.html"
    
    def get(self, request, *args, **kwargs):
        if 'method_id' in kwargs:
            try:
                data = MethodSummaryVW.objects.get(method_id=kwargs['method_id'])
            except MethodSummaryVW.DoesNotExist:
                data = None
                
            # Get analyte information including synonyms for each analyte
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
                
            notes = MethodAnalyteVW.objects.filter(method_id__exact=kwargs['method_id']).values('precision_descriptor_notes', 'dl_note').distinct()
            
            return self.render_to_response({'data': data,
                                            'analyte_data' : analyte_data,
                                            'notes' : notes})
        else:
            raise Http404
 
    
class ExportMethodAnalyte(View, TemplateResponseMixin):
    
    ''' Extends the standard view. This view creates a
    tab-separated file of the analyte data. Required keyword argument,
    method_id is used to retrieve the analyte information. This uses
    the same query that is used in the MethodSummaryView to retrieve
    the analyte data.
    '''

    def get(self, request, *args, **kwargs):
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
                
class BaseAnalyteSearchView(BaseSearchView):
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

class ExportAnalyteSearchView(ExportSearchMixin, BaseAnalyteSearchView):
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
    
    def get_valid_form_response(self, request, *args, **kwargs):
        return self.http_response(kwargs.get('export', '')) 

    def get_invalid_form_response(self, request, *args, **kwargs):
        return Http404
    
class AnalyteSearchView(BaseAnalyteSearchView, SearchResultMixin, TemplateResponseMixin):
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
        r_qs = super(AnalyteSearchView, self).get_results_context(qs)
        return [{'m' : r, 'greenness' : _greenness_profile(r)} for r in r_qs] 
    
    def get_valid_form_response(self, request, *args, **kwargs):
        self.context.update(self.get_valid_context(request, self.search_form, self.qs))
        return self.render_to_response(self.context)
    
    def get_invalid_form_response(self, request, *args, **kwargs):
        return self.render_to_response(self.get_invalid_context(request, self.search_form))
    
    def get_empty_form_response(self, request, *args, **kwargs):
        return self.render_to_response(self.get_invalid_context(request, self.form()))
    
    

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
        
class KeywordSearchView(View, TemplateResponseMixin):
    
    ''' This class extends the standard View to implement the keyword search view. This form only
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
'''        
class MicrobiologicalSearchView(SearchView, TemplateResponseMixin):
    
    template_name = "microbiological_search.html"
    form = MicrobiologicalSearchForm
    
    result_fields = ('method_id',
                     'source_method_identifier',
                     'method_descriptive_name',
                     'method_source',
                     'media_name',
                     'instrumentation_description',
                     'relative_cost_symbol',
                     'cost_effor_key')
    header_abbrev_set = ('SOURCE_METHOD_IDENTIFIER',
                         'METHOD_DESCRIPTIVE_NAME',
                         'METHOD_SOURCE',
                         'MEDIA_NAME',
                         'GEAR_TYPE',
                         'RELATIVE_COST')
    
    
'''    