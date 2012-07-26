
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from common.models import SourceCitationRef, CitationTypeRef
from common.utils.forms import get_criteria_from_field_data, get_criteria
from common.views import FilterFormMixin, SearchResultView
from forms import StatisticalSearchForm, StatisticalSourceEditForm

class AddStatisticalMethodView(CreateView):
    ''' Extends CreateView to implement the create statistical source page.
    '''
       
    template_name = 'create_statistic_source.html'
    form_class = StatisticalSourceEditForm
    model = SourceCitationRef
    
    def get_success_url(self):
        return reverse('sams-method_detail', kwargs={'pk' : self.object.source_citation_id})        
    
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
    
    def get_context_data(self, **kwargs):
        context = super(AddStatisticalMethodView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('sams-create_method')
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddStatisticalMethodView, self).dispatch(*args, **kwargs)
    
class UpdateStatisticalMethodListView(ListView):
    ''' Extends the standard ListView to implement the view which
    will show a list of views that the logged in user can edit.
    '''
    
    template_name = 'update_stat_source_list.html'
    context_object_name = 'source_methods'
    
    def get_queryset(self):
        if self.request.user.groups.filter(name__exact='nemi_admin'):
            qs = SourceCitationRef.stat_methods.all()
        
        else:
            qs = SourceCitationRef.stat_methods.filter(insert_person__exact=self.request.user)
            
        return qs.order_by('source_citation')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateStatisticalMethodListView, self).dispatch(*args, **kwargs)

class UpdateStatisticalMethodView(UpdateView):
    ''' Extends the standard UpdateView to implement the Update Statistical source page.'''
    
    template_name='update_statistic_source.html'
    form_class = StatisticalSourceEditForm
    model = SourceCitationRef
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateStatisticalMethodView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(UpdateStatisticalMethodView, self).get_context_data(**kwargs)
        context['insert_user'] = self.object.insert_person
        context['action_url'] = reverse('sams-update_method', kwargs={'pk': self.object.source_citation_id})
        return context

    def get_success_url(self):
        return reverse('sams-method_detail', kwargs={'pk' : self.object.source_citation_id})            

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
            
        if form.cleaned_data['analysis_type']:
            qs = qs.filter(analysis_types__exact=form.cleaned_data['analysis_type'])
            
        if form.cleaned_data['publication_source_type']:
            qs = qs.filter(sponser_types__exact=form.cleaned_data['publication_source_type'])
            
        if form.cleaned_data['study_objective']:
            qs = qs.filter(design_objectives__exact=form.cleaned_data['study_objective'])
            
        if form.cleaned_data['media_emphasized']:
            qs = qs.filter(media_emphasized__exact=form.cleaned_data['media_emphasized'])
            
        if form.cleaned_data['special_topic']:
            qs = qs.filter(special_topics__exact=form.cleaned_data['special_topic'])
            
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
    
    model = SourceCitationRef
    
    context_object_name = 'data'
    
class StatisticalMethodDetailView(DetailView):
    ''' Extends DetailView to implement the Statistical Source Detail view.'''
    
    template_name = 'statistical_source_detail.html'
    
    model = SourceCitationRef
    
    context_object_name = 'data'
