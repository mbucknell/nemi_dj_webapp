
import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db import connection, transaction
from django.db.models import Max, Model
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, FormView, View
from django.views.generic.edit import TemplateResponseMixin

from common.models import SourceCitationRef, Method, MethodOnline, MethodSubcategoryRef, MethodTypeRef, MethodStg, InstrumentationRef
from common.models import StatAnalysisRelStg,  StatDesignRelStg, StatTopicRelStg, StatMediaRelStg
from common.models import StatAnalysisRel, StatDesignRel, StatTopicRel, StatMediaRel
from common.utils.forms import get_criteria_from_field_data, get_criteria
from common.views import FilterFormMixin, SearchResultView
from forms import SAMSSearchForm, StatMethodEditForm


class AddStatMethodOnlineView(FormView):
    ''' Extends the FormView to implement the form to create a SAMs method using the StatMethodEditForm. The view prevents anyone who isn't
    logged in from accessing the view.
    '''
    
    template_name = 'create_statistic_source.html'
    form_class = StatMethodEditForm
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddStatMethodOnlineView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        #Save the source citation
        source_citation_id = SourceCitationRef.objects.aggregate(Max('source_citation_id'))['source_citation_id__max']
        if source_citation_id:
            source_citation_id = source_citation_id + 1
        else:
            source_citation_id = 1
        source_citation = SourceCitationRef(source_citation_id=source_citation_id)
        source_citation = form.get_source_citation_object(source_citation)
        
        source_citation.save()
        source_citation.sponser_types.add(*form.cleaned_data['sponser_types'])
        
        #Save the method and related objects
        method = MethodOnline(method_subcategory=MethodSubcategoryRef.objects.get(method_subcategory_id=16),
                              source_citation = source_citation,
                              method_type=MethodTypeRef.objects.get(method_type_id=3),
                              instrumentation=InstrumentationRef.objects.get(instrumentation='NA'),
                              insert_person_name=self.request.user.username,
                              insert_date=datetime.date.today(),
                              last_update_person_name=self.request.user.username,
                              last_update_date=datetime.date.today())
        method = form.get_method_object(method)
        
        method.save()
        
        for d in form.get_analysis_types(method.method_id):
            d.save()
        for d in form.get_design_objectives(method.method_id):
            d.save()
        for d in form.get_media_emphasized(method.method_id):
            d.save()
        for d in form.get_special_topics(method.method_id):
            d.save()
            
        return HttpResponseRedirect(reverse('sams-method_detail', kwargs={'pk' : method.method_id}))
    
    def get_context_data(self, **kwargs):
        '''Add the form's action_url to the context.'''
        context = super(AddStatMethodOnlineView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('sams-create_method')
        
        return context

    
class BaseUpdateStatisticalMethodView(FormView):
    '''Extends the FormView to implement an abstract view used to update SAMs methods.
    Methods can be updated at two stages: when they are in MethodOnline and when they are
    in MethodStg. This view is intended to be extended with using either MethodOnline or
    MethodStg as the model_class. Both models use the same *RelStg tables to save many to many 
    fields.
    '''
    
    form_class = StatMethodEditForm
    model_class = Model
    
    def get_initial(self):
        method = get_object_or_404(self.model_class, method_id=self.kwargs['pk'])
        result = {}
        
        result['source_method_identifier'] = method.source_method_identifier
        result['method_official_name'] = method.method_official_name
        result['method_source'] = method.method_source
        result['country'] = method.source_citation.country
        result['author'] = method.source_citation.author
        result['brief_method_summary'] = method.brief_method_summary
        result['table_of_contents'] = method.source_citation.table_of_contents
        result['publication_year'] = method.source_citation.publication_year
        result['source_citation_name'] = method.source_citation.source_citation_name
        result['link_to_full_method'] = method.link_to_full_method
        result['assumptions_comments'] = method.assumptions_comments
        result['item_type'] = method.source_citation.item_type
        result['item_type_note'] = method.source_citation.item_type_note
        result['sponser_types'] = list(method.source_citation.sponser_types.all())
        result['sponser_type_note'] = method.source_citation.sponser_type_note
        result['analysis_types'] = [t.analysis_type for t in StatAnalysisRelStg.objects.filter(method_id=method.method_id)]
        result['design_objectives'] = [t.design_objective for t in StatDesignRelStg.objects.filter(method_id=method.method_id)]
        result['sam_complexity'] = method.sam_complexity
        result['level_of_training'] = method.level_of_training
        result['media_emphasized'] = [t.media_name for t in StatMediaRelStg.objects.filter(method_id=method.method_id)]
        result['media_emphasized_note'] = method.media_emphasized_note
        result['media_subcategory'] = method.media_subcategory
        result['special_topics'] = [t.topic for t in StatTopicRelStg.objects.filter(method_id=method.method_id)]
        
        return result
    
    def form_valid(self, form):
        method = get_object_or_404(self.model_class, method_id=self.kwargs['pk'])
        
        source_citation = form.get_source_citation_object(method.source_citation) 
        source_citation.save()
        source_citation.sponser_types.clear()
        source_citation.sponser_types.add(*form.cleaned_data['sponser_types'])

        method = form.get_method_object(method)        
        method.last_update_person_name = self.request.user.username
        method.save()
        
        StatAnalysisRelStg.objects.filter(method_id=method.method_id).delete()
        StatDesignRelStg.objects.filter(method_id=method.method_id).delete()
        StatMediaRelStg.objects.filter(method_id=method.method_id).delete()
        StatTopicRelStg.objects.filter(method_id=method.method_id).delete()
        for d in form.get_analysis_types(method.method_id):
            d.save()
        for d in form.get_design_objectives(method.method_id):
            d.save()
        for d in form.get_media_emphasized(method.method_id):
            d.save()
        for d in form.get_special_topics(method.method_id):
            d.save()
            
        return HttpResponseRedirect(self.get_success_url())
    
    def get_action_url(self):
        ''' Override this method to define the action_url for the specific form.'''
        return ''
    
    def get_context_data(self, **kwargs):
        context = super(BaseUpdateStatisticalMethodView, self).get_context_data(**kwargs)
        context['insert_user'] = get_object_or_404(self.model_class, method_id=self.kwargs['pk']).get_insert_user()
        context['action_url'] = self.get_action_url()
        return context    
        
    
class UpdateStatMethodOnlineView(BaseUpdateStatisticalMethodView):
    '''Extends BaseUpdateStatisticalMethodView to implement the view which updates SAMs methods that are in the 
    MethodOnline table. 
    '''

    template_name = 'update_statistic_source.html'
    model_class = MethodOnline   
     
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatMethodOnlineView, self).dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('sams-method_detail', kwargs={'pk' : self.kwargs['pk']})
    
    def get_action_url(self):
        return reverse('sams-update_method', kwargs={'pk': self.kwargs['pk']})
    

class UpdateStatisticalMethodStgView(BaseUpdateStatisticalMethodView):
    '''Extends BaseUpdateStatisticalMethodView to implement the view which updates SAMs methods that are in the 
    MethodStg table. 
    '''
    
    template_name = 'update_statistic_source.html'
    model_class = MethodStg
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__exact='nemi_admin'),
                                       login_url='/sams/not_allowed/'))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatisticalMethodStgView, self).dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('sams-method_detail_for_approval', kwargs={'pk': self.kwargs['pk']})

    def get_action_url(self):
        return reverse('sams-update_review_method', kwargs={'pk': self.kwargs['pk']})
    
    
class UpdateStatisticalMethodOnlineListView(ListView):    
    ''' Extends the standard ListView to implement the view which
    will show a list of views that the logged in user can edit.
    '''
    
    template_name = 'update_stat_source_list.html'
    context_object_name = 'methods'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatisticalMethodOnlineListView, self).dispatch(request,*args, **kwargs)
    
    def get_queryset(self):
        result = MethodOnline.stat_methods.filter(insert_person_name=self.request.user.username).order_by('source_method_identifier')
        return result
        
class SubmitForReviewView(View, TemplateResponseMixin):
    '''Extends the standard View to implement, saving a method in MethodOnline to MethodStg and then
    deleting it from MethodOnline.
    '''
    
    template_name = 'submit_successful.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SubmitForReviewView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Set ready_to_review to 'Y', copy method from MethodOnline to MethodStg and then delete from MethodOnline
        method_online = get_object_or_404(MethodOnline,  method_id=self.kwargs['pk'])

        method_stg = MethodStg(method_id= method_online.method_id,
                               ready_for_review='Y',
                               last_update_person_name=request.user.username,
                               last_update_date=datetime.date.today(),
                               date_loaded=datetime.date.today(),
                               method_subcategory=method_online.method_subcategory,
                               method_source=method_online.method_source,
                               source_citation=method_online.source_citation,
                               source_method_identifier=method_online.source_method_identifier,
                               method_descriptive_name=method_online.method_descriptive_name,
                               method_official_name=method_online.method_official_name,
                               brief_method_summary=method_online.brief_method_summary,
                               link_to_full_method=method_online.link_to_full_method,
                               insert_date=method_online.insert_date,
                               insert_person_name=method_online.insert_person_name,                               
                               method_type=method_online.method_type,
                               assumptions_comments=method_online.assumptions_comments,
                               sam_complexity=method_online.sam_complexity,
                               level_of_training=method_online.level_of_training,
                               media_emphasized_note=method_online.media_emphasized_note,
                               media_subcategory=method_online.media_subcategory,
                               instrumentation=method_online.instrumentation)
        
        method_stg.save()
        method_online.delete()
        
        return self.render_to_response({'source_method_id' : method_stg.source_method_identifier})


class ReviewStatMethodStgListView(ListView):
    ''' Extends ListView to show all SAM methods in MethodStg that have not been approved.
    '''
    
    template_name='methods_for_review.html'
    context_object_name = 'methods'
    
    queryset = MethodStg.stat_methods.filter(approved='N').order_by('source_method_identifier')
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__exact='nemi_admin'),
                                       login_url='/sams/not_allowed/'))
    def dispatch(self, request, *args, **kwargs):
        return super(ReviewStatMethodStgListView, self).dispatch(request, *args, **kwargs)
    
    
class ApproveStatMethod(View, TemplateResponseMixin):
    ''' Extends the standard View to implement copying a method from MethodStg to the Method table.
    Methods are not removed from MethodStg, but it's approved flag is set to 'Y'.
    '''
    
    template_name="approve_method.html"

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__exact='nemi_admin'),
                                       login_url='/sams/not_allowed/'))
    def dispatch(self, request, *args, **kwargs):
        return super(ApproveStatMethod, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        method_stg = get_object_or_404(MethodStg, method_id=self.kwargs['pk'])
        today = datetime.date.today()
        
        # Set approved flag to 'Y' and approved_date, using raw SQL so that only those columns are updated.
        cursor = connection.cursor()
        cursor.execute('UPDATE method_stg SET approved = \'Y\', approved_date = %s WHERE method_id = %s', 
                       [today.strftime('%d-%b-%y'), method_stg.method_id])
        transaction.commit_unless_managed()
        
        # Copy method from MethodStg to Method        
        method = Method(method_id=method_stg.method_id,
                        last_update_person_name=request.user.username,
                        last_update_date=datetime.date.today(),
                        date_loaded=today,
                        approved='Y',
                        approved_date=today,
                        method_subcategory=method_stg.method_subcategory,
                        method_source=method_stg.method_source,
                        source_citation=method_stg.source_citation,
                        source_method_identifier=method_stg.source_method_identifier,
                        method_descriptive_name=method_stg.method_descriptive_name,
                        method_official_name=method_stg.method_official_name,
                        brief_method_summary=method_stg.brief_method_summary,
                        link_to_full_method=method_stg.link_to_full_method,
                        insert_date=method_stg.insert_date,
                        insert_person_name=method_stg.insert_person_name,                               
                        method_type=method_stg.method_type,
                        assumptions_comments=method_stg.assumptions_comments,
                        sam_complexity=method_stg.sam_complexity,
                        level_of_training=method_stg.level_of_training,
                        media_emphasized_note=method_stg.media_emphasized_note,
                        media_subcategory=method_stg.media_subcategory,
                        instrumentation=method_stg.instrumentation
                        )
        method.save()
        # First delete any instances that  currently exist in relational tables.
        # Then copy instances for the method from the relational tables from *Stg to * tables.
        StatAnalysisRel.objects.filter(pk=method_stg.method_id).delete()
        for t in StatAnalysisRelStg.objects.filter(method_id=method_stg.method_id):
            StatAnalysisRel.objects.create(method=method,
                                           analysis_type=t.analysis_type)
        
        StatDesignRel.objects.filter(pk=method_stg.method_id).delete()
        for t in StatDesignRelStg.objects.filter(method_id=method_stg.method_id):
            StatDesignRel.objects.create(method=method, 
                                         design_objective=t.design_objective)
            
        StatTopicRel.objects.filter(pk=method_stg.method_id).delete()
        for t in StatTopicRelStg.objects.filter(method_id=method_stg.method_id):
            StatTopicRel.objects.create(method=method,
                                        topic=t.topic)
        
        StatMediaRel.objects.filter(pk=method_stg.method_id).delete()
        for t in StatMediaRelStg.objects.filter(method_id=method_stg.method_id):
            StatMediaRel.objects.create(method=method,
                                        media_name=t.media_name)

        return self.render_to_response({'source_method_id' : method.source_method_identifier})
        
      
class StatisticSearchView(SearchResultView, FilterFormMixin):
    '''
    Extends the SearchResultView and FilterFormMixin to implement the view to display statistical methods.
    This view does not define any headers, therefore the template creates the table headers.
    '''
    
    template_name = 'statistic_search.html'
    form_class = SAMSSearchForm
    
    def get_qs(self, form):
        qs = Method.stat_methods.all()
        
        if form.cleaned_data['item_type']:
            qs = qs.filter(source_citation__item_type__exact=form.cleaned_data['item_type'])
            
        if form.cleaned_data['complexity'] != 'all':
            qs = qs.filter(sam_complexity__exact=form.cleaned_data['complexity'])
            
        if form.cleaned_data['analysis_type']:
            qs = qs.filter(statanalysisrel__analysis_type__exact=form.cleaned_data['analysis_type'])
            
        if form.cleaned_data['publication_source_type']:
            qs = qs.filter(source_citation__sponser_types__exact=form.cleaned_data['publication_source_type'])
            
        if form.cleaned_data['study_objective']:
            qs = qs.filter(statdesignrel__design_objective__exact=form.cleaned_data['study_objective'])
            
        if form.cleaned_data['media_emphasized']:
            qs = qs.filter(statmediarel__media_name__exact=form.cleaned_data['media_emphasized'])
            
        if form.cleaned_data['special_topic']:
            qs = qs.filter(stattopicrel__topic__exact=form.cleaned_data['special_topic'])
            
        return qs
            
    def get_context_data(self, form):
        criteria = []
        criteria.append(get_criteria_from_field_data(form, 'study_objective', label_override='What you are interested in'))
        criteria.append(get_criteria_from_field_data(form, 'item_type'))
        criteria.append(get_criteria(form['complexity']))
        criteria.append(get_criteria_from_field_data(form, 'analysis_type'))
        criteria.append(get_criteria_from_field_data(form, 'publication_source_type'))
        criteria.append(get_criteria_from_field_data(form, 'media_emphasized'))
        criteria.append(get_criteria_from_field_data(form, 'special_topic'))
        
        return {'criteria' : criteria}
        
    def get_header_defs(self):
        return None
        
    def get_results_context(self, qs):
        return {'results' : qs}
            
class StatisticalMethodSummaryView(DetailView):
    ''' Extends DetailView to implement the Statistical Source Summary view'''
    
    template_name = 'statistical_source_summary.html'
    
    model = Method
    
    context_object_name = 'data'
    
class BaseStatMethodStgDetailView(DetailView):
    '''Extends the DetailView to show a method object. This is intended to be extended using MethodOnline or MethodStg
    to show a detailed view of the object.
    '''
    
    context_object_name = 'data'

    def get_object(self, queryset=None):
        '''Conceptually the m2m tables belong with the method object, so redefine
        this method to return a dictionary containing method, analysis_types, design_objectives, media_emphasized, and special_topics
        ''' 
        result = {'method' : super(BaseStatMethodStgDetailView, self).get_object(queryset)}
        result['analysis_types'] = StatAnalysisRelStg.objects.filter(method_id=result['method'].method_id)
        result['design_objectives'] = StatDesignRelStg.objects.filter(method_id=result['method'].method_id)
        result['media_emphasized'] = StatMediaRelStg.objects.filter(method_id=result['method'].method_id)
        result['special_topics'] = StatTopicRelStg.objects.filter(method_id=result['method'].method_id)
        
        return result        


class StatisticalMethodOnlineDetailView(BaseStatMethodStgDetailView):
    ''' Extends DetailView to implement the Statistical Source Detail view.'''
    
    template_name = 'statistical_source_detail.html'
    model = MethodOnline
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StatisticalMethodOnlineDetailView, self).dispatch(request, *args, **kwargs)

        
class StatisticalMethodStgDetailView(BaseStatMethodStgDetailView):
    
    template_name = 'statistical_method_review_detail.html'
    model = MethodStg
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name__exact='nemi_admin'),
                                       login_url='/sams/not_allowed/'))
    def dispatch(self, request, *args, **kwargs):
        return super(StatisticalMethodStgDetailView, self).dispatch(request, *args, **kwargs)
    
