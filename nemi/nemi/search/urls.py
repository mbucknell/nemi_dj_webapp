
''' This module contains the url conf for the nemi search pages.
'''

from django.conf.urls.defaults import patterns, url
import views;

urlpatterns = patterns("", 
        url(r'^general_search/$',
            views.GeneralSearchView.as_view(),
            name='search-general'),
        url(r'^general_search_tsv/$',
            views.GeneralSearchView.as_view(),
            {'^export' : 'tsv'},
            name='search-general_export_tsv'),
        url(r'^general_search_xls/$',
            views.GeneralSearchView.as_view(),
            {'^export' : 'xls'},
            name='search-general_export_xls'),
        url(r'^greenness_profile/(?P<pk>\d+)/$',
            views.GreennessView.as_view(),
            name='search-greenness'),
        url(r'^method_summary/(?P<method_id>\d+)/$',
            views.MethodSummaryView.as_view(),
            name='search-method_summary'),
        url(r'^method_source/(?P<pk>\d+)/$',
            views.MethodSourceView.as_view(),
            name='search-method_source'),
        url(r'^citation_information/(?P<pk>\d+)/$',
            views.CitationInformationView.as_view(),
            name='search-citation_information'),
        url(r'^header_definition/(?P<abbrev>\w+)/$',
            views.HeaderDefinitionsView.as_view(),
            name='search-header_definitions'),
        url(r'^synonyms/$',
            views.SynonymView.as_view(),
            name='search-synonyms'),
        url(r'^analyte_search/$', 
            views.AnalyteSearchView.as_view(),
            name='search-analyte_search'),
        url(r'^analyte_select/$',
            views.AnalyteSelectView.as_view(),
            name='search-analyte_select'),
        )