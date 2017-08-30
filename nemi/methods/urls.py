
''' This module contains the url conf for the NEMI method pages.
'''

from django.conf.urls import url

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    url(r'^keyword/$',
        views.KeywordResultsView.as_view(),
        name='methods-keyword'),
    url(r'^browse_methods/$',
        views.BrowseMethodsView.as_view(),
        name='methods-browse'),
    url(r'^results/$',
        views.MethodResultsView.as_view(),
        name='methods-results'),
    url(r'^analyte_results/$',
        views.AnalyteResultsView.as_view(),
        name='methods-analyte_results'),
    url(r'^statistical_results/$',
        views.StatisticalResultsView.as_view(),
        name='methods-statistical_results'),
    url(r'^regulatory_results/$',
        views.RegulatoryResultsView.as_view(),
        name='methods-regulatory_results'),

    url(r'^export_results/$',
        views.ExportMethodResultsView.as_view(),
        name='methods-export_results'),
    url(r'^export_analyte_results/$',
        views.ExportAnalyteResultsView.as_view(),
        name='methods-export_analyte_results'),
    url(r'^export_statistical_results/$',
        views.ExportStatisticalResultsView.as_view(),
        name='methods-export_statistical_results'),
    url(r'^export_regulatory$',
        views.ExportRegulatoryResultsView.as_view(),
        name='methods-export_regulatory_results'),

    url(r'^method_summary/(?P<method_id>\d+)/$',
        views.MethodSummaryView.as_view(),
        name='methods-method_summary'),
    url(r'^method_analyte_export/(?P<method_id>\w+)/$',
        views.ExportMethodAnalyte.as_view(),
        name='methods-method_analyte_export'),
    url(r'^sams_method_summary/(?P<pk>\d+)/$',
        views.StatisticalMethodSummaryView.as_view(),
        name='methods-sam_method_summary'),

    url(r'^method_pdf/(?P<method_id>\d+)/$',
        views.MethodPdfView.as_view(),
        name='methods-pdf'),
    url(r'^revision_pdf/(?P<revision_id>\d+)/$',
        views.RevisionPdfView.as_view(),
        name='revision-pdf'),

    ## Ajax urls which return json objects
    url(r'^analyte_select/$',
        views.AnalyteSelectView.as_view(),
        name='methods-analyte_select'),
    url(r'^method_count/$',
        views.MethodCountView.as_view(),
        name='methods-method_count'),
    url(r'^media_name/$',
        views.MediaNameView.as_view(),
        name='methods-media_name'),
    url(r'^method_source/$',
        views.SourceView.as_view(),
        name='methods-source'),
    url(r'^instrumentation/$',
        views.InstrumentationView.as_view(),
        name='methods-instrumentation'),
    url(r'^method_types/$',
        views.MethodTypeView.as_view(),
        name='methods-method_types'),
    url(r'^subcategories/$',
        views.SubcategoryView.as_view(),
        name='methods-subcategories'),
    url(r'^gear_types/$',
        views.GearTypeView.as_view(),
        name='methods-gear_types'),
    url(r'^stat_objectives/$',
        views.StatObjectiveView.as_view(),
        name='methods-stat_objectives'),
    url(r'^stat_item_types/$',
        views.StatItemTypeView.as_view(),
        name='methods-stat_item_types'),
    url(r'^stat_analysis_types/$',
        views.StatAnalysisTypeView.as_view(),
        name='methods-stat_analysis_types'),
    url(r'^stat_source_type/$',
        views.StatSourceTypeView.as_view(),
        name='methods-stat_publication_source'),
    url(r'^stat_media_emphasized/$',
        views.StatMediaNameView.as_view(),
        name='methods-stat_media_emphasized'),
    url(r'^stat_special_topics/$',
        views.StatSpecialTopicsView.as_view(),
        name='methods-stat_special_topics'),

    url(r'^wqp/(?P<op>[A-Za-z0-9-_/]*)/$',
        views.WQPWebProxyView.as_view(),
        name='wqp_proxy'),
]

router = routers.SimpleRouter()
router.register(r'api/methods', views.MethodRestViewSet, 'method')

api_urlpatterns = format_suffix_patterns(router.urls, allowed=['json', 'html'])
