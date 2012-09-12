from django.forms import Form
from django.views.generic import View, DetailView
from django.views.generic.edit import TemplateResponseMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Q

from common.views import FilterFormMixin, SearchResultView
from common.utils.forms import get_criteria_from_field_data, get_criteria
from models import SensorInfoVw, AnalyteListACT, AnalyteInfo, SensorInfoVw, SensorsACT, MethodAnalyteACT
from models import MethodSensorAnalyteListACT, MethodSensorListACT, MethodAnalyteVw
from forms import MemoAnalyteSearchForm, MemoCombinedSearchForm, MemoSensorSearchForm

class MemoAnalyteSearchView(SearchResultView, FilterFormMixin):
	'''
	Extends the SearchResultView and FilterFormMixin to implement the view to
	search and display sensors filtered by analyte.	 This view does not define
	any headers, therefore the template creates the table headers.
	'''
	
	template_name = 'memo_analyte_search.html'
	form_class = MemoAnalyteSearchForm
	
	def get_qs(self, form):
		qs = SensorInfoVw.objects.all()
		
		if form.cleaned_data['analyte']:
			qs = qs.filter(analyte_name__exact=form.cleaned_data['analyte'])
			
		return qs
		
	def get_context_data(self, form):
		criteria = []
		criteria.append(get_criteria_from_field_data(form, 'analyte'))
		
		try:
			if form.cleaned_data['analyte']:
				desc = AnalyteInfo.objects.filter(analyte_id__exact=form.cleaned_data['analyte'].analyte_id)[0]
			else:
				desc = 'No information available for this analyte'
		except IndexError:
			desc = 'No information available for this analyte'
		
		return {'criteria' : criteria, 'description' : desc}
		
	def get_header_defs(self):
		return None
	
	def get_results_context(self, qs):
		return {'results': qs}
		
class MemoCombinedSearchView(SearchResultView, FilterFormMixin):
	'''
	Extends the SearchResultView and FilterFormMixin to implement the view
	to search and display sensors filtered by analyte or method.
	'''
	
	template_name = 'memo_combined_search.html'
	form_class = MemoCombinedSearchForm
	
	def get_qs(self, form):
		qs = SensorInfoVw.objects.all()
		
		if form.cleaned_data['analyte']:
			qs = qs.filter(analyte_id__exact=form.cleaned_data['analyte'])
		if form.cleaned_data['method']:
			qs = qs.filter(method_id__exact=form.cleaned_data['method'])
		
		return qs
		
	def get_context_data(self, form):
		criteria = []		
		method_qs = MethodAnalyteVw.objects.all()
		
		if form.cleaned_data['analyte']:
			criteria.append(('Analyte', MethodSensorAnalyteListACT.objects.values('analyte_id', 'analyte_name').distinct().get(analyte_id__exact=(form.cleaned_data['analyte']))['analyte_name']))
			method_qs = method_qs.filter(analyte_id__exact=form.cleaned_data['analyte'])
		if form.cleaned_data['method']:			
			criteria.append(('Method', MethodSensorListACT.objects.values('method_id', 'method_no').distinct().get(method_id__exact=(form.cleaned_data['method']))['method_no']))
			method_qs = method_qs.filter(method_id__exact=form.cleaned_data['method'])
		
		return {'criteria': criteria, 'methods': method_qs}
		
	def get_header_defs(self):
		return None
	
	def get_results_context(self, qs):
		return {'results': qs}
		
class MemoSensorSearchView(SearchResultView, FilterFormMixin):
	'''
	Extends the SearchResultView and FilterFormMixin to implement the view
	to search and display sensors filtered by analyte or manufacturer.
	'''

	template_name = 'memo_sensor_search.html'
	form_class = MemoSensorSearchForm

	def get_qs(self, form):
		qs = SensorInfoVw.objects.all()

		if form.cleaned_data['analyte']:
			qs = qs.filter(analyte_id__exact=form.cleaned_data['analyte'])
		if form.cleaned_data['mfr']:
			q_array = []
			for mfr in form.cleaned_data['mfr']:
				q_array.append(Q(manufacturer__icontains=mfr))
			
			final_q = q_array[0]
			for i in range(1, len(q_array)):
				final_q = final_q | q_array[i]
				
			qs = qs.filter(final_q)
		return qs

	def get_context_data(self, form):
		criteria = []

		if form.cleaned_data['analyte']:
			criteria.append(('Analyte', MethodSensorAnalyteListACT.objects.values('analyte_id', 'analyte_name').distinct().get(analyte_id__exact=(form.cleaned_data['analyte']))['analyte_name']))
		if form.cleaned_data['mfr']:
			mfrs = []
			for mfr in form.cleaned_data['mfr']:
				mfrs.append(mfr)
				
			criteria.append(('Manufacturer', ' OR '.join(mfrs)))

		return {'criteria': criteria}

	def get_header_defs(self):
		return None

	def get_results_context(self, qs):
		return {'results': qs}
		
class MemoSensorDetailView(DetailView):
	'''
	Extends the DetailView class to implement a detail view for sensors.
	We have to override get_context_data to get data from another model.
	'''
	template_name = 'sensor_detail.html'
	model = SensorsACT
	context_object_name = 'sensor'
	
	def get_context_data(self, **kwargs):
		context = super(MemoSensorDetailView, self).get_context_data(**kwargs)
		
		context['method'] = get_object_or_404(MethodAnalyteACT, fm_pk_sensorid__exact=self.kwargs['pk'])
		
		return context
		
class MemoAnalyteListView(View):
	'''
	Extends the View class to return a JSON string containing the appropriate Analyte options
	for Combined Search, when provided with a method ID.
	'''
	
	def get(self, request, *args, **kwargs):
		if request.GET:
			if (request.GET['method']):
				qs = MethodSensorAnalyteListACT.objects.filter(method_id__exact=request.GET['method']).order_by('analyte_name').values('analyte_name', 'analyte_id').distinct()
			else:
				qs = MethodSensorAnalyteListACT.objects.order_by('analyte_name').values('analyte_name', 'analyte_id').distinct()
				
			qs_array = ('"%s" : "%s"' % (v['analyte_id'], v['analyte_name']) for v in qs)
			qs_str = '{ "" : "Any", ' + ', '.join(qs_array) + '}'
			return HttpResponse(qs_str, mimetype='application/json')
				
		return HttpResponse('{ "empty": true ' + '}', mimetype="application/json")

class MemoMethodListView(View):
	'''
	Extends the View class to return a JSON string containing the appropriate Method options
	for Combined Search, when provided with a analyte ID.
	'''
	
	def get(self, request, *args, **kwargs):
		if request.GET:
			if (request.GET['analyte']):
				qs = MethodSensorListACT.objects.filter(analyte_id__exact=request.GET['analyte']).order_by('method_no').values('method_id', 'method_no').distinct()
			else:
				qs = MethodSensorListACT.objects.order_by('method_no').values('method_id', 'method_no').distinct()
			
			qs_array = ('"%s" : "%s"' % (v['method_id'], v['method_no']) for v in qs)
			qs_str = '{ "" : "Any", ' + ', '.join(qs_array) + '}'
			return HttpResponse(qs_str, mimetype='application/json')
				
		return HttpResponse('{ "empty": true ' + '}', mimetype="application/json")
		
class MemoMfrAnalyteListView(View):
	'''
	Extends the View class to return a JSON string containing the appropriate Analyte options
	for Sensor Search, when provided with a manufacturer.
	'''
	
	def get(self, request, *args, **kwargs):
		if (request.GET and 'mfr[]' in request.GET):
			if (request.GET['mfr[]']):
				qs = SensorInfoVw.objects
				
				q_array = []
				for tup in request.GET.lists():
					if (tup[0] == 'mfr[]'):
						for mfr in tup[1]:
							q_array.append(Q(manufacturer__icontains=mfr))
				
				final_q = q_array[0]
				for i in range(1, len(q_array)):
					final_q = final_q | q_array[i]
					
				qs = qs.filter(final_q).order_by('analyte_name')
				qs = qs.values('analyte_name', 'analyte_id').distinct()
			else:
				qs = SensorInfoVw.objects.order_by('analyte_name').values('analyte_name', 'analyte_id').distinct()
				
			qs_array = ('"%s" : "%s"' % (v['analyte_id'], v['analyte_name']) for v in qs)
			qs_str = '{ "" : "Any", ' + ', '.join(qs_array) + '}'
			return HttpResponse(qs_str, mimetype='application/json')
				
		return HttpResponse('{ "empty": true ' + '}', mimetype="application/json")
		
class MemoMfrListView(View):
	'''
	Extends the View class to return a JSON string containing the appropriate Manufacturer options
	for Sensor Search, when provided with an analyte id.
	'''

	def get(self, request, *args, **kwargs):
		if request.GET:
			if (request.GET['analyte']):
				qs = SensorInfoVw.objects.filter(analyte_id__exact=request.GET['analyte']).order_by('manufacturer').values('manufacturer').distinct()
			else:
				qs = SensorInfoVw.objects.order_by('manufacturer').values('manufacturer').distinct()

			qs_array = ('"%s" : "%s"' % (v['manufacturer'], v['manufacturer']) for v in qs)
			qs_str = '{ "" : "Any", ' + ', '.join(qs_array) + '}'
			return HttpResponse(qs_str, mimetype='application/json')

		return HttpResponse('{ "empty": true ' + '}', mimetype="application/json")