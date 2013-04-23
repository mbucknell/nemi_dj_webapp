'''
Created on Jul 25, 2012

@author: mbucknel
'''
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns("", 
        url(r'^method_summary/(?P<pk>\d+)/$',
            views.StatisticalMethodSummaryView.as_view(),
            name='sams-method_summary'),
        url(r'^create_method/$',
            views.AddStatMethodOnlineView.as_view(),
            name='sams-create_method'),
        url(r'^update_method_list/$',
            views.UpdateStatisticalMethodOnlineListView.as_view(),
            name='sams-update_method_list'),
        url(r'^method_detail/(?P<pk>\d+)/$',
            views.StatisticalMethodOnlineDetailView.as_view(),
            name='sams-method_detail'),
        url(r'^update_method/(?P<pk>\d+)/$',
            views.UpdateStatMethodOnlineView.as_view(),
            name='sams-update_method'),
        url(r'^method_submission/(?P<pk>\d+)/$',
            views.SubmitForReviewView.as_view(),
            name='sams-submit_for_review'),
        url(r'^method_review_list/$',
            views.ReviewStatMethodStgListView.as_view(),
            name='sams-method_review_list'),
        url(r'^method_review_detail/(?P<pk>\d+)/$',
            views.StatisticalMethodStgDetailView.as_view(),
            name='sams-method_detail_for_approval'),
        url(r'^update_review_method/(?P<pk>\d+)/$',
            views.UpdateStatisticalMethodStgView.as_view(),
            name='sams-update_review_method'),
        url(r'^approve_method/(?P<pk>\d+)/$',
            views.ApproveStatMethod.as_view(),
            name='sams-approve_method'),
        url(r'^method_entry/$',
            views.MethodEntryRedirectView.as_view(),
            name='sams-method_entry'),
)