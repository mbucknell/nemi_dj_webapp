from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns("",
	url(r'^analyte_search/$',
	views.MemoAnalyteSearchView.as_view(),
	name='memo-analyte_search'),
	
	url(r'^combined_search/$',
	views.MemoCombinedSearchView.as_view(),
	name='memo-combined_search'),
	
	url(r'^sensor_search/$',
	views.MemoSensorSearchView.as_view(),
	name='memo-sensor_search'),
	
	url(r'^sensor_summary/(?P<pk>\d+)/$',
	views.MemoSensorDetailView.as_view(),
	name='memo-sensor_details'),
	
	url(r'^analyte_list/$',
	views.MemoAnalyteListView.as_view(),
	name='memo-analyte_list'),
	
	url(r'^method_list/$',
	views.MemoMethodListView.as_view(),
	name='memo-method_list'),
	
	url(r'^mfr_analyte_list/$',
	views.MemoMfrAnalyteListView.as_view(),
	name='memo-mfr_analyte_list'),
	
	url(r'^mfr_list/$',
	views.MemoMfrListView.as_view(),
	name='memo-mfr_list')
)