''' This module includes the view functions which implement the various
search pages.
'''

# standard python packages
import types

# django packages
from django.db.models import Model, Q
from django.forms import Form
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import TemplateResponseMixin

# Provides conversion to Excel format
from xlwt import Workbook

# project specific packages
from forms import GeneralSearchForm, AnalyteSearchForm, AnalyteSelectForm
from models import MethodVW, MethodSummaryVW, MethodAnalyteVW, DefinitionsDOM, AnalyteCodeRel, MethodAnalyteAllVW

def _choice_select(field):
    '''Return the visible choice from the form field variable. The function
    assumes choice values are integer or string
    '''
    if type(field.field.choices[1][0]) is types.IntType:
        return dict(field.field.choices).get(int(field.data))
    return dict(field.field.choices).get(field.data)

def _greenness_profile(d):
    '''Return a list of four gifs representing the greenness profile of the dictionary d.
    If there is not enough information for a complete greenness profile list, return an empty list.
    '''
    pbt = d.get('pbt', '')
    toxic = d.get('toxic', '')
    corrosive = d.get('toxic', '')
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
        
    if len(g) == 4:
        return g
    else:
        return []
    
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

class SearchView(View):

    ''' Extends the generic mixin to handle method search pages 
    Optional keyword arguments are:
    export -- kind is either tsv or xls and if specified the query results are used to 
              produce the indicated file.
              
    If export is not specified, the queryset is passed back to the view with the results of
    the derived query. Additional context information can be generated in the same procedure,
    get_query_and context_from_form, that generates the query set.
    '''
    
    form = Form #Search form which generates the result query set
    
    result_fields = () # Fields to be displayed on the results page
    result_field_order_by = '' #Field to order the query results. If null, no order is specified
    
    export_fields = () # Fields to be exported to file
    export_field_order_by = '' # Field name to order the export query results by. If null, no order is specified
   
    def get_query_and_context_from_form(self):
        '''Generate the query set that is a derived from the form along with any additional context
        data that is required from the form.
        This function assumes that the form has been validated.
        '''
        self.qs = None
        self.context = {}
        
    def get(self, request, *args, **kwargs):
        ''' Processes the get request. This method should not need to be overridden.'''
        if request.GET:
            self.search_form = self.form(request.GET)
            if self.search_form.is_valid():
                self.get_query_and_context_from_form()
                
                if 'export' in kwargs:
                    # Export data to the requested file kind
                    HEADINGS = [name.replace('_', ' ').title() for name in self.export_fields]
                    self.qs = self.qs.values_list(*self.export_fields).distinct()
                    if self.export_field_order_by:
                        self.qs = self.qs.order_by(self.export_field_order_by)
                    
                    if kwargs['export'] == 'tsv':
                        return _tsv_response(HEADINGS, self.qs)
                    
                    if kwargs['export'] == 'xls':
                        return _xls_response(HEADINGS, self.qs)
                    
                    else:
                        return Http404
                    
                else:
                    # Get data to display on page.
                    self.qs = self.qs.values(*self.result_fields).distinct()
                    if self.result_field_order_by:
                        self.qs = self.qs.order_by(self.result_field_order_by)
                    #Determine Greenness rating if any
                    results = []
                    for m in self.qs:
                        results.append({'m': m, 'greenness' : _greenness_profile(m)})
    
                    # Get the query string and pass to view to form the export urls.        
                    fpath = request.get_full_path()
                    query_string = '?' + fpath.split('&',1)[1] 
                    
                    self.context['results'] = results
                    self.context['search_form'] = self.search_form
                    self.context['hide_search'] = True
                    self.context['show_results'] = True
                    self.context['query_string'] = query_string
                    
                    return self.render_to_response(self.context) 
                
            else:
                # There is an error in validation so resubmit the search form
                return self.render_to_response({'search_form' : self.search_form,
                                                'hide_search' : False,
                                                'show_results' : False
                                                })
                
        else:
            #Show an empty form
            self.search_form = self.form()
            return self.render_to_response({'search_form' : self.search_form,
                                            'hide_search' : False,
                                            'show_results' : False})
           
class GeneralSearchView(SearchView, TemplateResponseMixin):
    
    '''Extends the SearchView to implement the General Search Page. '''
    
    template_name = 'general_search.html'
    form = GeneralSearchForm
    
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
                 
class GreennessView(DetailView):

    '''Extends the DetailView using model MethodVW with keyword argument pk'''
    
    model = MethodVW
    template_name = 'greenness_profile.html'
    context_object_name = 'data'

class MethodSummaryView(View, TemplateResponseMixin):
    
    ''' Extends the standard view. This view only processes GET requests. The
    keyword argument method_id is used to retrieve the MethodSummaryVW and MethodAnalyteVW information
    '''

    template_name="method_summary.html"
    
    def get(self, request, *args, **kwargs):
        if 'method_id' in kwargs:
            data = get_object_or_404(MethodSummaryVW, method_id=kwargs['method_id'])
            analyte_data = MethodAnalyteVW.objects.filter(preferred__exact=-1, method_id__exact=kwargs['method_id']).order_by('analyte_name')
            analyte_data = analyte_data.values('analyte_name',
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
            notes = MethodAnalyteVW.objects.filter(method_id__exact=kwargs['method_id']).values('precision_descriptor_notes', 'dl_note').distinct()
            
            return self.render_to_response({'data': data,
                                            'analyte_data' : analyte_data,
                                            'notes' : notes})
        else:
            raise Http404
 
class MethodSourceView(DetailView):
    
    ''' Extends the DetailView for the MethodSummaryVW and keyword argument pk'''
    
    model = MethodSummaryVW
    template_name = 'method_source.html'
    context_object_name = 'data'
    
class CitationInformationView(DetailView):
    
    '''Extends the DetailView for the MethodSummaryVW model and keyword argument pk'''
    
    model = MethodSummaryVW
    template_name = 'citation_information.html'
    context_object_name = 'data' 
    
class HeaderDefinitionsView(DetailView):
    
    ''' Extends the DetailView for the DefintionsDOM model.
    The view shows the object with the definition_abbrev contained
    in keyword argument 'abbrev'.
    '''
    
    model = DefinitionsDOM
    template_name = 'header_definitions.html'
    context_object_name = 'data'
    
    def get_object(self):
        try:
            return self.get_queryset().get(definition_abbrev=self.kwargs.get('abbrev', None))
        except(self.model.MultipleObjectsReturned, self.model.DoesNotExist):
            return None

class SynonymView(ListView):
    
    '''Extends the ListView using the queryset returned from the get_queryset function.
    Also adds the analyte name and code to the context data. These are retrieved from 
    keyword arguments.
    '''
    
    template_name = 'synonyms.html'
    context_object_name = 'qs'
    
    def get_queryset(self):
        ''' Return the queryset of analyte synonyms by using both the specific analyte's name and code to search.'''
        name = self.request.GET.get('name', None).lower()
        code = self.request.GET.get('code', None).lower()
        inner_qs = AnalyteCodeRel.objects.filter(Q(analyte_name__iexact=name)|Q(analyte_code__iexact=code)).values_list('analyte_code', flat=True).distinct()
        qs = AnalyteCodeRel.objects.all().filter(analyte_code__in=inner_qs).order_by('analyte_name').values('analyte_name')
        return qs
    
    def get_context_data(self, **kwargs):
        ''' Add the analyte name and code to the context data'''
        context = super(SynonymView, self).get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', None)
        context['code'] = self.request.GET.get('code', None)
        return context

class AnalyteSearchView(SearchView, TemplateResponseMixin):
    
    ''' Extends the SearchView to implement the Analyte Search page '''
    
    template_name = 'analyte_search.html'
    
    form = AnalyteSearchForm
    
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