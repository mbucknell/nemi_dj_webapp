import types

from django.core.urlresolvers import reverse
from django.db.models import Model, Q
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import TemplateResponseMixin

from xlwt import Workbook

from forms import GeneralSearchForm
from models import MethodVW, MethodSummaryVW, MethodAnalyteVW, DefinitionsDOM, AnalyteCodeRel

class GeneralSearchView(View, TemplateResponseMixin):
    
    template_name = 'general_search.html'
    
    def get(self, request, *args, **kwargs):
        def _choice_select(field):
            if type(field.field.choices[1][0]) is types.IntType:
                return dict(field.field.choices).get(int(field.data))
            return dict(field.field.choices).get(field.data)
        
        if request.GET:
            search_form = GeneralSearchForm(request.GET)
            if search_form.is_valid():
                # Create queryset from form data
                qs = MethodVW.objects.all()
                criteria = []
                if search_form.cleaned_data['media_name'] != 'all':
                    qs = qs.filter(media_name__exact=search_form.cleaned_data['media_name'])
                    criteria.append((search_form['media_name'].label, _choice_select(search_form['media_name'])))
     
                if search_form.cleaned_data['source'] != 'all':
                    qs = qs.filter(method_source__contains=search_form.cleaned_data['source'])
                    criteria.append((search_form['source'].label, _choice_select(search_form['source'])))
                                    
                if search_form.cleaned_data['method_number'] != 'all':
                    qs = qs.filter(method_id__exact=int(search_form.cleaned_data['method_number']))
                    criteria.append((search_form['method_number'].label, _choice_select(search_form['method_number'])))
                    
                if search_form.cleaned_data['instrumentation'] != 'all':
                    qs = qs.filter(instrumentation_id__exact=int(search_form.cleaned_data['instrumentation']))  
                    criteria.append((search_form['instrumentation'].label, _choice_select(search_form['instrumentation'])))
                
                if search_form.cleaned_data['method_subcategory'] != 'all':
                    qs = qs.filter(method_subcategory_id__exact=int(search_form.cleaned_data['method_subcategory']))
                    criteria.append((search_form['method_subcategory'].label, _choice_select(search_form['method_subcategory'])))
                    
                method_type_dict = dict(search_form['method_types'].field.choices)
                if len(search_form.cleaned_data['method_types']) == len(method_type_dict):
                    selected_method_types = []
                else:
                    selected_method_types = [method_type_dict.get(int(k)) for k in search_form.cleaned_data['method_types']]
                
                qs = qs.filter(method_type_id__in=search_form.cleaned_data['method_types'])
                    
                if 'export' in kwargs:
                    # Create file for tab separated
                    HEADINGS = ('Method ID', 
                                'Source Method Identifier', 
                                'Method Descriptive Name', 
                                'Media Name', 
                                'Method Source', 
                                'Instrumentation Description',
                                'Method Subcategory',
                                'Method Category',
                                'Method Type')
                    qs = qs.values_list('method_id', 
                                        'source_method_identifier',
                                        'method_descriptive_name', 
                                        'media_name', 
                                        'method_source',
                                        'instrumentation_description',
                                        'method_subcategory',
                                        'method_category',
                                        'method_type_desc').order_by('source_method_identifier')
                    if kwargs['export'] == 'tsv':
                        response = HttpResponse(mimetype='text/tab-separated-values')
                        response['Content-Disposition'] = 'attachment; filename=general_search.tsv'
                    
                        response.write('\t'.join(HEADINGS))
                        response.write('\n')
                    
                        for row in qs:
                            for col in row:
                                response.write('%s\t' % str(col))
                            response.write('\n')
                    
                        return response
                    
                    if kwargs['export'] == 'xls':
                        response = HttpResponse(mimetype='application/vnd.ms-excel')
                        response['Content-Disposition'] = 'attachment; filename=general_search.xls'
                        
                        wb = Workbook()
                        ws = wb.add_sheet('sheet 1')
                        
                        for col_i in range(len(HEADINGS)):
                            ws.write(0, col_i, HEADINGS[col_i])
                        
                        for row_i in range(len(qs)):
                            for col_i in range(len(qs[row_i])):
                                ws.write(row_i + 1, col_i, qs[row_i][col_i])
                        
                        wb.save(response)
                        
                        return response
                    
                    else: 
                        return Http404
                else:    
                    qs = qs.values('source_method_identifier',
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
                                   'waste'
                                   ).distinct()
        
                    # Determine Greenness rating if any 
                    results = []
                    for m in qs:
                        g = []
                        if m['pbt'] == 'N':
                            g.append('ULG2.gif')
                        elif m['pbt'] == 'Y':
                            g.append('ULW2.gif')
                            
                        if m['toxic'] == 'N':
                            g.append('URG2.gif')
                        elif m['toxic'] == 'Y':
                            g.append('URW2.gif')
                            
                        if m['corrosive'] == 'N':
                            g.append('LLG2.gif')
                        elif m['corrosive'] == 'Y':
                            g.append('LLW2.gif')
                            
                        if m['waste'] == 'N':
                            g.append('LRG2.gif')
                        elif m['waste']== 'Y':
                            g.append('LRW2.gif')
                            
                        if len(g) == 4:
                            results.append({'m': m, 'greenness' : g})
                        else:
                            results.append({'m': m, 'greenness' : []})
                            
                    fpath = request.get_full_path()
                    query_string = '?' + fpath.split('&',1)[1]  
                                        
                    return self.render_to_response({'search_form' : search_form,
                                                    'results' : results,
                                                    'criteria' : criteria,
                                                    'selected_method_types' : selected_method_types,
                                                    'hide_search': True,
                                                    'query_string' : query_string,
                                                    })
            else:
                return self.render_to_response({'search_form' : search_form})
        else:
            search_form = GeneralSearchForm()
            return self.render_to_response({'search_form' : search_form})        

        
class GreennessView(DetailView):
    model = MethodVW
    template_name = 'greenness_profile.html'
    context_object_name = 'data'

class MethodSummaryView(View, TemplateResponseMixin):

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
    model = MethodSummaryVW
    template_name = 'method_source.html'
    context_object_name = 'data'
    
class CitationInformationView(DetailView):
    model = MethodSummaryVW
    template_name = 'citation_information.html'
    context_object_name = 'data' 
    
class HeaderDefinitionsView(DetailView):
    model = DefinitionsDOM
    template_name = 'header_definitions.html'
    context_object_name = 'data'
    
    def get_object(self):
        try:
            return self.get_queryset().get(definition_abbrev=self.kwargs.get('abbrev', None))
        except(self.model.MultipleObjectsReturned, self.model.DoesNotExist):
            return None

class SynonymView(ListView):
    template_name = 'synonyms.html'
    context_object_name = 'qs'
    
    def get_queryset(self):
        name = self.request.GET.get('name', None).lower()
        code = self.request.GET.get('code', None).lower()
        inner_qs = AnalyteCodeRel.objects.filter(Q(analyte_name__iexact=name)|Q(analyte_code__iexact=code)).values_list('analyte_code', flat=True).distinct()
        qs = AnalyteCodeRel.objects.all().filter(analyte_code__in=inner_qs).order_by('analyte_name').values('analyte_name')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super(SynonymView, self).get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', None)
        context['code'] = self.request.GET.get('code', None)
        return context
