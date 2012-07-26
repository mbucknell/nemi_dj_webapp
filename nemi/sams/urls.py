'''
Created on Jul 25, 2012

@author: mbucknel
'''
from django.conf.urls import patterns, url
import views

urlpatterns = patterns("", 
        url(r'^search/$',
            views.StatisticSearchView.as_view(),
            name='sams-statistics'),
        url(r'^method_summary/(?P<pk>\d+)/$',
            views.StatisticalMethodSummaryView.as_view(),
            name='sams-method_summary'),
        url(r'^create_method/$',
            views.AddStatisticalMethodView.as_view(),
            name='sams-create_method'),
        url(r'^update_method_list/$',
            views.UpdateStatisticalMethodListView.as_view(),
            name='sams-update_method_list'),
        url(r'^method_detail/(?P<pk>\d+)/$',
            views.StatisticalMethodDetailView.as_view(),
            name='sams-method_detail'),
        url(r'^update_method/(?P<pk>\d+)/$',
            views.UpdateStatisticalMethodView.as_view(),
            name='sams-update_method'),
)