
''' This module contains the url conf for the NEMI protocol services and pages.
'''
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^browse/$',
        views.BrowseProtocolsView.as_view(),
        name='protocols-browse'),
    url(r'^protocol_count/$',
        views.ProtocolCountView.as_view(),
        name='protocols-protocol_count'),
    url(r'^protocol_summary/(?P<pk>\d+)/$',
        views.ProtocolSummaryView.as_view(),
        name='protocols-summary'),
]
