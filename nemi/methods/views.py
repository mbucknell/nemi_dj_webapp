''' This module includes the view functions which implement the various
NEMI methods pages.
'''

import re

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, DetailView
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.edit import TemplateResponseMixin

# project specific packages
from common.models import MethodAnalyteVW, InstrumentationRef, StatisticalDesignObjective, StatisticalItemType
from common.models import StatisticalAnalysisType, StatisticalSourceType, MediaNameDOM, StatisticalTopics
from common.models import StatAnalysisRel, SourceCitationRef, StatDesignRel, StatMediaRel, StatTopicRel, Method
from common.utils.view_utils import dictfetchall, xls_response, tsv_response
from common.views import PdfView, ChoiceJsonView

from domhelp.views import FieldHelpMixin

from .models import MethodVW, MethodSummaryVW, AnalyteCodeRel, MethodAnalyteAllVW, AnalyteCodeVW, RevisionJoin, RegQueryVW


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

def _clean_keyword(k):
    ''' Returns keyword with special characters and quotes properly escaped. These cause the keyword
    search to fail unless properly escaped
    '''
    escape_pattern = re.compile(r'(?P<esc>[-\,])')
    quote_pattern = re.compile(r'(?P<quote>[\'\"])')
    
    result = re.sub(escape_pattern, r'\\\g<esc>', k)
    result = re.sub(quote_pattern, r'\g<quote>\g<quote>', result)
    
    return result


class AnalyteSelectView(View):
    ''' Extends the standard view to implement a view which returns json data containing
    a list of the matching analyte values in values_list key.
    '''
    
    def get(self, request, *args, **kwargs):
        if request.GET:
            if request.GET['kind'] == 'code':
                if request.GET['selection']:
                    qs = AnalyteCodeVW.objects.filter(
                        analyte_analyte_code__icontains=request.GET['selection']).order_by('analyte_analyte_code').values_list('analyte_analyte_code', 
                                                                                                                               flat=True).distinct()
                    qs_str = '[' + ', '.join('"%s"' % v for v in qs) + ']'
                else:
                    return HttpResponse('{"values_list" : ""}', mimetype="application/json")
                
            else:
                category = request.GET.get('category', '')
                subcategory = request.GET.get('subcategory', '')    
                if category != '' or subcategory != '':
                    qs = MethodAnalyteAllVW.objects.all()
                    if category != '':
                        qs = qs.filter(method_category__iexact=category)
                    if subcategory != '':
                        qs = qs.filter(method_subcategory__iexact=subcategory)
                                            
                elif request.GET['selection']:
                    qs = AnalyteCodeRel.objects.filter(analyte_name__icontains=request.GET['selection'])
                    
                else:
                    return HttpResponse('{"values_list" : ""}', mimetype="application/json")
                    
                qs = qs.values_list('analyte_name', 'analyte_code').distinct().order_by('analyte_name');
                qs_str='[' +', '.join('["%s","%s"]' % (n, c) for (n, c) in qs) + ']'
            
            return HttpResponse('{"values_list" : ' +  qs_str+ '}', mimetype="application/json")
            
        return HttpResponse('{"values_list" : ""}', mimetype="application/json")
 
        
class MethodCountView(View):
    '''
    Extends the standard View to retrieve and return as a json object the total number of methods in the datastore.
    '''
    
    def get(self, request, *args, **kwargs):
        return HttpResponse('{"method_count" : "' + str(MethodVW.objects.count()) + '"}', mimetype="application/json");

  
class MediaNameView(ChoiceJsonView):
    '''
    Extends the ChoiceJsonView to retrieve the media names as a json object
    '''
    def get_choices(self, request, *args, **kwargs):
        return [(m[0], m[0].capitalize()) for m in MethodVW.objects.filter(media_name__isnull=False).values_list('media_name').distinct().order_by('media_name')]

    
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
    
        sc_qs = qs.values_list('method_source', 'method_source_name').distinct().filter(method_source_name__isnull=False).exclude(method_source__contains='EPA').exclude(method_source__contains='USGS').exclude(method_source__startswith='DOE')
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
        
    


class ResultsMixin(MultipleObjectMixin):
    '''
    Extends the MultipleObjectMixin to implement the standard filters for method result searches. 
    This can be mixed with other classes which provide the response handling. The queryset attribute 
    should be specified when extending this class.
    '''
    
    context_object_name = 'data'
    
    def get_queryset (self):
        data = self.queryset
        
        if 'category' in self.request.GET and self.request.GET.get('category'):
            data = data.filter(method_category__iexact=self.request.GET.get('category'))
        if 'subcategory' in self.request.GET and self.request.GET.get('subcategory'):
            data = data.filter(method_subcategory__in=self.request.GET.getlist('subcategory'))
    
        media_name = self.request.GET.get('media_name', '')
        source = self.request.GET.get('source', '')
        instrumentation = self.request.GET.get('instrumentation', '')
        if media_name != '':
            data = data.filter(media_name__exact=media_name)
        if source != '':
            data = data.filter(method_source__contains=source)
        if instrumentation != '':
            data = data.filter(instrumentation_id__exact=instrumentation)
            
        if 'method_type' in self.request.GET:
            data = data.filter(method_type_desc__in=self.request.GET.getlist('method_type'))
        
        return data
    
    
class BaseResultsView(TemplateResponseMixin, View):
    '''
    Extends the standard View and TemplateResponse to implement the view which will return method
    results while adding a context variable to be used to specify the page's export_url.
    The view can be mixed with a child of ResultsMixin to implement method result page views or any
    mixin containing a get_queryset method and a get_context_data method.
    ''' 
    
    export_url = None ## Optional - url which will be used to download the contents of the results page. 
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)
        if self.export_url:
            context['export_url'] = self.export_url
        return self.render_to_response(context)
    
    
class ExportBaseResultsView(View):
    '''
    Extends the standard View to implement a view which returns downloads method results. The view
    can be mixed with a child of ResultsMixin to implement method result page download results or any
    mixin containing a get_queryset method.
    '''
    
    export_fields = () #Define fields to be written to the download field. Tuple of strings.
    filename = None #Download field name string.
    
    def get(self, request, *args, **kwargs):
        if request.GET:
            HEADINGS = [name.replace('_', ' ').title() for name in self.export_fields]
            export_type = kwargs.get('export', 'xls')
            
            vl_qs = self.get_queryset().filter(method_id__in=self.request.GET.getlist('method_id', [])).values_list(*self.export_fields)
         
            if export_type == 'tsv':
                return tsv_response(HEADINGS, vl_qs, self.filename)
                    
            elif export_type == 'xls':
                return xls_response(HEADINGS, vl_qs, self.filename)
            
            else:
                raise Http404
        else:
            raise Http404   


class MethodResultsMixin(ResultsMixin):
    '''
    Extend ResultsMixin to implement the querying part of the results view for methods.
    '''
    
    queryset = MethodVW.objects.all()
    
    def get_queryset(self):
        data = super(MethodResultsMixin, self).get_queryset()
        
        if 'method_number' in self.request.GET:
            data = data.filter(source_method_identifier__contains=self.request.GET.get('method_number'))
        
        matrix = self.request.GET.get('matrix', '')
        if matrix != '':
            data = data.filter(matrix__exact=matrix)
        return data

    
class MethodResultsView(MethodResultsMixin, FieldHelpMixin, BaseResultsView):
    '''
    Extends MethodResultsMixin and BaseResultsView to implement the method results page.
    '''
    
    template_name = 'methods/method_results.html'    
    export_url = reverse_lazy('methods-export_results')
    field_names = ['source_method_identifier',
                 'method_source',
                 'method_descriptive_name',
                 'method_subcategory',
                 'instrumentation_description',
                 'media_name',
                 'method_category',
                 'method_type_desc',
                 'matrix',
                 'relative_cost_symbol']

    
class ExportMethodResultsView(MethodResultsMixin, ExportBaseResultsView):
    '''
    Extend MethodResultsMixin and ExportBaseResultsView to implement the download method results view.
    '''
    
    export_fields = ('method_id', 
                     'source_method_identifier',
                     'method_descriptive_name', 
                     'media_name', 
                     'method_source',
                     'instrumentation_description',
                     'instrumentation',
                     'method_subcategory',
                     'method_category',
                     'method_type_desc',
                     'matrix',
                     'relative_cost',
                     'relative_cost_symbol')
       
    filename = 'method_results'
       

class AnalyteResultsMixin(ResultsMixin):
    '''
    Extend ResultsMixin to implement the querying part of the analyte results for methods.
    '''
 
    queryset = MethodAnalyteAllVW.objects.all()
    
    def get_queryset(self):
            data = super(AnalyteResultsMixin, self).get_queryset()
            
            if 'analyte_name' in self.request.GET and self.request.GET.get('analyte_name'):
                names = self.request.GET.getlist('analyte_name')
                data = data.filter(analyte_name__iregex=r'(' + '|'.join(['^' + re.escape(n) + '$' for n in names]) + ')')
                
            elif 'analyte_code' in self.request.GET and self.request.GET.get('analyte_code'):
                codes = self.request.GET.getlist('analyte_code')
                data = data.filter(analyte_code__iregex=r'(' + '|'.join(['^' + re.escape(c) + '$' for c in codes]) + '$)')
                
            else:
                data = data.filter(preferred__exact=-1) # Only get the method for the preferred analyte
                analyte_type = self.request.GET.get('analyte_type', '')
                waterbody_type = self.request.GET.get('waterbody_type', '')
                gear_type = self.request.GET.get('gear_type', '')
    
                if analyte_type != '':
                    data = data.filter(analyte_type__exact=analyte_type)                        
                if waterbody_type != '':
                    data = data.filter(waterbody_type__exact=waterbody_type)   
                if gear_type != '':
                    data = data.filter(instrumentation_id__exact=gear_type)
             
            return data.values('method_source_id',
                         'method_id',
                         'source_method_identifier',
                         'method_source',
                         'method_descriptive_name',
                         'method_subcategory',
                         'method_source_id',
                         'method_source_contact',
                         'method_source_url',
                         'method_type_desc',
                         'method_descriptive_name',
                         'media_name',
                         'waterbody_type',
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
                         'false_positive_value',
                         'false_negative_value',
                         'dl_units',
                         'instrumentation_description',
                         'instrumentation',
                         'relative_cost',
                         'relative_cost_symbol',
                         'cost_effort_key',
                         'matrix',
                         'pbt',
                         'toxic',
                         'corrosive',
                         'waste',
                         'assumptions_comments',
                         'analyte_name',
                         'analyte_code',
                         ).distinct()    
       
class AnalyteResultsView(AnalyteResultsMixin, FieldHelpMixin, BaseResultsView):
    '''
    Extends AnalyteResultsMixin and BaseResultsView to implement the method results by analyte page.
    '''
    
    template_name = 'methods/analyte_results.html'
    export_url = reverse_lazy('methods-export_analyte_results')
    
    field_names = ['source_method_identifier',
                   'method_source',
                   'method_descriptive_name',
                   'analyte_name',
                   'dl_value',
                   'dl_type',
                   'accuracy',
                   'precision',
                   'prec_acc_conc_used',
                   'false_positive_value',
                   'false_negative_value',
                   'instrumentation_description',
                   'relative_cost',
                   'media_name',
                   'method_type_desc',
                   'waterbody_type']
    

class ExportAnalyteResultsView(AnalyteResultsMixin, ExportBaseResultsView):
    '''
    Extend AnalyteResultsMixin and ExportBaseResultsView to implement the download method results by analyte.
    '''

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
    
    filename = 'analyte_results'    
               
class StatisticalResultsMixin(ResultsMixin):
    '''
    Extend ResultsMixin to implement the querying part of the results for statistical methods.
    '''
    
    queryset = MethodVW.objects.all()
    
    def get_queryset(self):
        data = super(StatisticalResultsMixin, self).get_queryset()
        
        item_type = self.request.GET.get('item_type', '')
        complexity = self.request.GET.get('complexity', '')
        analysis_type = self.request.GET.get('analysis_type', '')
        publication_source_type = self.request.GET.get('publication_source_type', '')
        study_objective = self.request.GET.get('study_objective', '')
        media_emphasized = self.request.GET.get('media_emphasized', '')
        special_topic = self.request.GET.get('special_topic', '')
        
        if item_type != '':
            data = data.filter(source_citation_id__in=SourceCitationRef.objects.filter(item_type__exact=item_type).values('source_citation_id'))
        if complexity != '':
            data = data.filter(sam_complexity__exact=complexity)
        if analysis_type != '':
            data = data.filter(method_id__in=StatAnalysisRel.objects.filter(analysis_type__exact=analysis_type).values('method_id'))
        if publication_source_type != '':
            data = data.filter(source_citation_id__in=SourceCitationRef.objects.filter(publicationsourcerel__source__exact=publication_source_type).values('source_citation_id'))
        if study_objective != '':
            data = data.filter(method_id__in=StatDesignRel.objects.filter(design_objective__exact=study_objective).values('method_id'))
        if media_emphasized != '':   
            data = data.filter(method_id__in=StatMediaRel.objects.filter(media_name__exact=media_emphasized).values('method_id'))
        if special_topic != '':
            data = data.filter(method_id__in=StatTopicRel.objects.filter(topic__exact=special_topic).values('method_id'))
        
        return data
    
class StatisticalResultsView(StatisticalResultsMixin, FieldHelpMixin, BaseResultsView):
    '''
    Extends StatisticalResultsMixin and BaseResultsView to implement the statistical method results page.
    '''
        
    template_name = 'methods/statistical_results.html' 
    export_url = reverse_lazy('methods-export_statistical_results')
    
    field_names = ['author',
                   'title',
                   'publication_year',
                   'method_source',
                   'link_to_full_method']
    
class ExportStatisticalResultsView(StatisticalResultsMixin, ExportBaseResultsView):           
    '''
    Extend StatisticalResultsMixin and ExportBaseResultsView to implement the download statistical method results.
    '''

    export_fields = ('method_id',
                     'method_descriptive_name',
                     'method_subcategory',
                     'method_category',
                     'method_source',
                     'source_method_identifier',
                     'method_official_name',
                     'author',
                     'publication_year',
                     'sam_complexity',
                     )
            
    filename = 'statistical_method_results'
    
    
class RegulatoryResultsMixin(ResultsMixin):
    '''
    Extends the Results Mixin to implement regulatory method search. 
    '''
    
    queryset = RegQueryVW.objects.exclude(method_subcategory__in=['SAMPLE/PREPARATION', 'GENERAL'])
    
    def get_queryset(self):
        data = self.queryset
        
        if 'analyte_name' in self.request.GET and self.request.GET.get('analyte_name'):
            names = self.request.GET.get('analyte_name').splitlines()
            data = data.filter(analyte_name__iregex=r'(' + '|'.join(['^' + re.escape(n) + '$' for n in names]) + ')')
            
        elif 'analyte_code' in self.request.GET and self.request.GET.get('analyte_code'):
            codes = self.request.GET.get('analyte_code').splitlines()
            data = data.filter(analyte_code__iregex=r'(' + '|'.join(['^' + re.escape(c) + '$' for c in codes]) + '$)')
       
        return data.order_by('regulation', 'method_source', 'source_method_identifier')           
        
class RegulatoryResultsView(RegulatoryResultsMixin, FieldHelpMixin, BaseResultsView):
    '''Extends the mixins to implement the regulatory results view.
    '''
    
    template_name = 'methods/regulatory_results.html' 
    export_url = reverse_lazy('methods-export_regulatory_results')
    
    field_names = ['regulation',
                   'reg_location',
                   'method_source',
                   'source_method_identifier',
                   'revision_information',
                   'method_descriptive_name',
                   'dl_value',
                   'dl_type',
                   'instrumentation_description',
                   'relative_cost'
                   ]


class ExportRegulatoryResultsView(RegulatoryResultsMixin, ExportBaseResultsView):
    '''
    Extends the ExportBaseResultView with RegulatoryResultsMixin to provide an Excel file for download.
    '''

    export_fields = ('regulation',
                     'regulation_name',
                     'reg_location',
                     'method_source',
                     'source_method_identifier',
                     'method_id',
                     'method_descriptive_name',
                     'revision_information',
                     'dl_value',
                     'dl_units',
                     'dl_type',
                     'instrumentation',
                     'instrumentation_description',
                     'relative_cost_symbol',
                     'relative_cost'
                     );
            
    filename = 'regulatory_method_results'
    

class KeywordResultsView(TemplateResponseMixin, View):
    '''Extends the standard View to implement the keyword search view. This form only
    processes get requests.
    '''  
    
    template_name = "methods/keyword_search.html"
    
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
                clean_keyword = _clean_keyword(keyword)
                # Execute as raw query since  it uses a CONTAINS clause and context grammer.
                cursor = connection.cursor() #@UndefinedVariable
                cursor.execute('SELECT DISTINCT score(1) method_summary_score, mf.method_id, mf.source_method_identifier method_number, \
mf.link_to_full_method, mf.mimetype, mf.revision_id, mf.method_official_name, mf.method_descriptive_name, mf.method_source, mf.method_category \
FROM nemi_data.method_fact mf, nemi_data.revision_join rj \
WHERE mf.revision_id = rj.revision_id AND \
(CONTAINS(mf.source_method_identifier, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + clean_keyword + '<progression> \
<seq><rewrite>transform((TOKENS, "{", "}", " "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "AND"))</rewrite></seq>\
</progression></textquery><score datatype="INTEGER" algorithm="COUNT"/></query>\', 1) > 1 \
OR CONTAINS(rj.method_pdf, \'<query><textquery lang="ENGLISH" grammar="CONTEXT">' + clean_keyword + '<progression> \
<seq><rewrite>transform((TOKENS, "{", "}", " "))</rewrite></seq>\
<seq><rewrite>transform((TOKENS, "{", "}", "AND"))</rewrite></seq>\
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
                                                'results' : results,
                                                'total_found' : len(results_list)})
            
        else:
            #Render a blank form
            return self.render_to_response({})
        
class BrowseMethodsView(ListView):
    '''
    Extends ListView to implement the browse all methods page. Methods are sorted by category, subcategory, 
    and identifier.
    '''
    template_name = 'methods/browse_methods.html'
    
    queryset = MethodVW.objects.order_by('method_category', 'method_subcategory', 'source_method_identifier')
    
    
class MethodSummaryView(FieldHelpMixin, DetailView):
    '''
    Extends the DetailView to provide the method summary view. 
    '''
    
    template_name='methods/method_summary.html'
    context_object_name = 'method'
    
    # Field definitions to be used in the method summary view to provide table definitions.
    field_names = ['method_official_name',
                   'media_name',
                   'instrumentation_description',
                   'method_subcategory',
                   'method_source',
                   'source_citation_information',
                   'brief_method_summary',
                   'scope_and_application',
                   'applicable_conc_range',
                   'interferences',
                   'qc_requirements',
                   'sample_handling',
                   'max_holding_time',
                   'relative_cost',
                   'sample_prep_methods']
    
    def get_object(self):
        ''' Override get_object to return the method details, method analytes, and method notes.
        The returned object is a dictionary.
        '''
        result = {};
        if 'method_id' in self.kwargs:
            try:
                result['details'] = MethodSummaryVW.objects.get(method_id=self.kwargs['method_id'])
                
            except MethodSummaryVW.DoesNotExist:
                result['details'] = None
            
            # Get associated analyted data
            result['analytes'] = []
            
            analyte_qs = _analyte_value_qs(self.kwargs['method_id'])
            for r in analyte_qs:
                name = r['analyte_name'].lower()
                code = r['analyte_code'].lower()
                inner_qs = AnalyteCodeRel.objects.filter(Q(analyte_name__iexact=name)|Q(analyte_code__iexact=code)).values_list('analyte_code', flat=True).distinct()
                qs = AnalyteCodeRel.objects.all().filter(analyte_code__in=inner_qs).order_by('analyte_name').values('analyte_name')
                syn = []
                for a in qs:
                    syn.append(a['analyte_name'])
                    
                result['analytes'].append({'r' : r, 'syn' : syn})  
            
            #Get description notes    
            result['notes'] = MethodAnalyteVW.objects.filter(method_id__exact=self.kwargs['method_id']).values('precision_descriptor_notes', 'dl_note').distinct()
                
            #Get revision information
            result['latest_revision'] = RevisionJoin.objects.get(revision_id=result['details'].revision_id)
            result['revisions'] = RevisionJoin.objects.filter(method_id__exact=self.kwargs['method_id']).order_by('-revision_id')
            
            return result         
        else:
            raise Http404
               
            
class StatisticalMethodSummaryView(FieldHelpMixin, DetailView):
    ''' Extends DetailView to implement the Statistical Source Summary view'''
    
    template_name = 'sams/statistical_source_summary.html'
    model = Method
    context_object_name = 'data'
    
    field_names = ['title',
                   'author',
                   'abstract_summary',
                   'table_of_contents',
                   'source_citation_name',
                   'method_source',
                   'citation_country',
                   'publication_year',
                   'notes',
                   'source_citation_item_type',
                   'publication_source',
                   'purpose',
                   'design_objectives',
                   'sam_complexity',
                   'media_emphasized',
                   'media_subcategory',
                   'special_topics'
                   ]
    
    
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
        

class MethodPdfView(PdfView):
    ''' 
    Extends the PdfView to serve a method's pdf file if it it exists in the database.
    '''
    
    def get_pdf_info(self):
        cursor = connection.cursor()
        cursor.execute('SELECT mimetype, method_pdf, source_method_identifier from nemi_data.method_summary_vw where method_id=%s',
                       [self.kwargs['method_id']])
        results_list = dictfetchall(cursor)
        if results_list:
            self.mimetype = results_list[0]['MIMETYPE']
            self.pdf = results_list[0]['METHOD_PDF']
            self.filename = _clean_name(results_list[0]['SOURCE_METHOD_IDENTIFIER'])
    
        

class RevisionPdfView(PdfView):
    '''
    Extends PdfView to serve a revision's pdf file if it exists in the database.
    '''
    def get_pdf_info(self):
        cursor = connection.cursor()
        cursor.execute('SELECT mimetype, method_pdf, revision_information from nemi_data.revision_join where revision_id=%s', [self.kwargs['revision_id']])
        results_list = dictfetchall(cursor)
        
        if results_list:
            self.mimetype = results_list[0]['MIMETYPE'] 
            self.pdf = results_list[0]['METHOD_PDF']
            self.filename = self.kwargs['revision_id']
