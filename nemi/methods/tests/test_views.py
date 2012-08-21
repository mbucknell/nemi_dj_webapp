'''
Created on Mar 13, 2012

@author: mbucknel
'''
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import unittest

from methods.views import GeneralSearchView, AnalyteSearchView, MicrobiologicalSearchView, BiologicalSearchView, ToxicitySearchView, PhysicalSearchView
from methods.views import StreamPhysicalSearchView, RegulatorySearchView, TabularRegulatorySearchView
from methods.views import _clean_name

class TestCleanName(unittest.TestCase):

    def test_clean_name(self):
        name = 'a256&B*-_Z'
        self.assertEqual(name, _clean_name(name))
        
        name = 'a<sub>3</sub>43ABc'
        self.assertEqual('a343ABc', _clean_name(name))
        
        name = 'a(3)43ABC'
        self.assertEqual('a343ABC', _clean_name(name))
        
        name = 'a#343ABC'
        self.assertEqual('a343ABC', _clean_name(name))
        
        name = 'a 343ABC'
        self.assertEqual('a_343ABC', _clean_name(name))
        
        name = 'a3,4,3ABC'
        self.assertEqual('a3_4_3ABC', _clean_name(name))
        
        name = 'a3/43/ABC'
        self.assertEqual('a3_43_ABC', _clean_name(name)) 
        
        name = 'a3/43.ABC'
        self.assertEqual('a3_43_ABC', _clean_name(name))
        
        name = 'a3<sub>4</sub>3 ABC'
        self.assertEqual('a343_ABC', _clean_name(name))
           

class TestGeneralSearchView(TestCase):
    fixtures = ['definitions_dom.json', 'method_vw.json']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-general'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : 'all',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 16)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_by_media_name(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'AIR',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : 'all',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Media name','Air'), None, None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_by_method_number(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : '4845',
                               'instrumentation' : 'all',
                               'method_subcategory' : 'all',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, ('Method number','Po-01-RC (DOE EML)'), None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_by_instrumentation(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : '41',
                               'method_subcategory' : 'all',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None ,('Instrumentation','Pulse Ionization Chamber and Radon Bubbler'), None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_by_method_subcategory(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : '4',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None , None, ('Method subcategory','Radiochemical')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 4)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_by_method_types(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : 'all',
                               'method_types' : [2]
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(GeneralSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None , None, None])
        self.assertEqual(resp.context['selected_method_types'], ['Sample Collection'])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]['m']), len(GeneralSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])
        
    def test_view_filter_invalid(self):
        resp = self.client.get(reverse('methods-general'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : 'all',
                               'method_types' : []
                               })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'general_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        

class TestExportGeneralSearchView(TestCase):
    fixtures = ['method_vw.json']
    
    def test_view_output_tsv(self):
        resp = self.client.get(reverse('methods-general_export_tsv'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : '4',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'text/tab-separated-values')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=general_search.tsv')
        
    def test_view_output_xls(self):
        resp = self.client.get(reverse('methods-general_export_xls'),
                               {'media_name' : 'all',
                               'source' : 'all',
                               'method_number' : 'all',
                               'instrumentation' : 'all',
                               'method_subcategory' : '4',
                               'method_types' : [1, 2, 5, 10]
                               })
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'application/vnd.ms-excel')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=general_search.xls')
        
    def test_view_bad_query(self):
        resp = self.client.get(reverse('methods-general_export_xls'))
        self.assertEqual(resp.status_code, 404)      
          
class TestAnalyteSearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_analyte_all_vw.json', 
                'media_name_dom.json', 
                'method_source_ref.json', 
                'instrumentation_ref.json',
                'method_subcategory_ref.json',
                'method_vw.json']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-analyte'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_analyte(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : '',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_with_analyte_name(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name', 'Po'), None, None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        

    def test_view_with_analyte_code(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'code',
                                'analyte_value' : '7440-08-6',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte code', '7440-08-6'), None, None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        

    def test_view_with_analyte_name_and_media_name(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'WATER',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name', 'Po'), ('Media name', 'Water'), None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        

    def test_view_with_analyte_name_and_instrumentation(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : '3',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name', 'Po'), None, None, ('Instrumentation', 'Alpha Scintillation'), None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        
                
    def test_view_with_analyte_name_and_method_subcategory(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : '2',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation', 'Toxicity Test Procedure']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name', 'Po'), None, None, None, ('Method subcategory', 'Inorganic')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        
                
    def test_view_with_analyte_name_and_method_types(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Collection']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(AnalyteSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name', 'Po'), None, None, None, None])
        self.assertEqual(resp.context['selected_method_types'], ['Sample Collection'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['m']), len(AnalyteSearchView.result_fields))
        self.assertIn('greenness', resp.context['results'[0]])        
                
    def test_view_no_method_types(self):
        resp = self.client.get(reverse('methods-analyte'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : '',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : []})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'analyte_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
                         
class TestExportAnalyteSearchView(TestCase):
    fixtures = ['method_analyte_all_vw.json',
                'media_name_dom.json', 
                'method_source_ref.json', 
                'instrumentation_ref.json',
                'method_subcategory_ref.json',
                'method_vw.json'
                ]
    
    def test_view_output_tsv(self):
        resp = self.client.get(reverse('methods-analyte_export_tsv'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation']
                               })
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'text/tab-separated-values')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=analyte_search.tsv')
        
    def test_view_output_xls(self):
        resp = self.client.get(reverse('methods-analyte_export_xls'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Po',
                                'media_name' : 'all',
                                'source' : 'all',
                                'instrumentation' : 'all',
                                'method_subcategory' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection', 'Sample Processing/Preparation']
                               })
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'application/vnd.ms-excel')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=analyte_search.xls')
        
    def test_view_bad_query(self):
        resp = self.client.get(reverse('methods-analyte_export_xls'))
        self.assertEqual(resp.status_code, 404)
        
class TestAnalyteSelectView(TestCase):
    fixtures = ['analyte_code_vw',
                'analyte_code_rel']
    
    def test_bad_query(self):
        resp = self.client.get(reverse('methods-analyte_select'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertEqual(resp.content, '{"values_list" : ""}')        
    
    def test_blank_selection(self):
        resp = self.client.get(reverse('methods-analyte_select'), 
                               {'selection' : '',
                                'kind' : 'name'}) 
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertEqual(resp.content, '{"values_list" : ""}')
        
    def test_analyte_name(self):
        resp = self.client.get(reverse('methods-analyte_select'),
                               {'selection' : 'Po',
                                'kind' : 'name'
                                })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertEqual(resp.content, '{"values_list" : ["Po", "Polonium"]}')
        
    def test_analyte_code(self):
        resp = self.client.get(reverse('methods-analyte_select'),
                               {'selection' : '7440-41-7',
                                'kind' : 'code'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertEqual(resp.content, '{"values_list" : ["7440-41-7"]}')
        
class TestMicrobiologicalSearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_analyte_all_vw.json',
                'method_vw.json']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-microbiological'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'microbiological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-microbiological'),
                               {'analyte' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Processing/Preparation']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'microbiological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(MicrobiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(MicrobiologicalSearchView.result_fields))
       
    def test_view_analyte_filter(self):
        resp = self.client.get(reverse('methods-microbiological'),
                               {'analyte' : '19609',
                                'method_types' : ['Sample Analysis', 'Sample Processing/Preparation']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'microbiological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(MicrobiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte name (code)','Sulfate-reducing Bacteria (N-55652)')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(MicrobiologicalSearchView.result_fields))
       
    def test_view_method_types_filter(self):
        resp = self.client.get(reverse('methods-microbiological'),
                               {'analyte' : 'all',
                                'method_types' : ['Sample Processing/Preparation']})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'microbiological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(MicrobiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['selected_method_types'], ['Sample Processing/Preparation'])
        self.assertEqual(len(resp.context['results']), 0)
        
    def test_view_no_method_types(self):
        resp = self.client.get(reverse('methods-microbiological'),
                               {'analyte' : 'all',
                                'method_types' : []})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'microbiological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
        
class TestBiologicalSearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_analyte_all_vw.json',
                'instrumentation_ref.json',
                'method_vw.json']
       
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-biological'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte_type' : 'all',
                                'waterbody_type' : 'all',
                                'gear_type' : 'all',
                                'method_types' : ['Sample Collection', 'Sample Processing/Preparation']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(BiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(BiologicalSearchView.result_fields))
        
    def test_view_analyte_type_filter(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte_type' : 'Macroinvertebrate',
                                'waterbody_type' : 'all',
                                'gear_type' : 'all',
                                'method_types' : ['Sample Collection', 'Sample Processing/Preparation']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(BiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte type', 'Macroinvertebrate'), None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(BiologicalSearchView.result_fields))          
        
    def test_view_waterbody_type_filter(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte_type' : 'all',
                                'waterbody_type' : 'Wadeable stream',
                                'gear_type' : 'all',
                                'method_types' : ['Sample Collection', 'Sample Processing/Preparation']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(BiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, ('Waterbody type', 'Wadeable stream'), None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(BiologicalSearchView.result_fields))          
        
    def test_view_gear_type_filter(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte_type' : 'all',
                                'waterbody_type' : 'all',
                                'gear_type' : '112',
                                'method_types' : ['Sample Collection', 'Sample Processing/Preparation']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(BiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, ('Gear type', 'Seine')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(BiologicalSearchView.result_fields))  
        
    def test_view_method_types_filter(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte_type' : 'all',
                                'waterbody_type' : 'all',
                                'gear_type' : 'all',
                                'method_types' : ['Sample Collection']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(BiologicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None])
        self.assertEqual(resp.context['selected_method_types'], ['Sample Collection'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(BiologicalSearchView.result_fields))                  
                        
    def test_view_no_method_types(self):
        resp = self.client.get(reverse('methods-biological'),
                               {'analyte' : 'all',
                                'waterbody_type' : 'all',
                                'gear_type' : 'all',
                                'method_types' : []})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
                        
class TestToxicitySearchView(TestCase):
    fixtures = ['defintions_dom.json',
                'method_analyte_all_vw.json',
                'method_vw.json']

    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-toxicity'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'all',
                                'media' : 'all',
                                'matrix' : 'all',
                                'method_types' : ['Toxicity Test Procedure', 'Sample Analysis']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(ToxicitySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 3)
        self.assertEqual(len(resp.context['results'][0]), len(ToxicitySearchView.result_fields))

    def test_view_subcategory_filter(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'Biotoxin',
                                'media' : 'all',
                                'matrix' : 'all',
                                'method_types' : ['Toxicity Test Procedure', 'Sample Analysis']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(ToxicitySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Subcategory', 'Biotoxin'), None, None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(ToxicitySearchView.result_fields))
                                
    def test_view_media_filter(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'all',
                                'media' : 'WATER',
                                'matrix' : 'all',
                                'method_types' : ['Toxicity Test Procedure', 'Sample Analysis']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(ToxicitySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, ('Media', 'Water'), None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(ToxicitySearchView.result_fields))
                                
    def test_view_matrix_filter(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'all',
                                'media' : 'all',
                                'matrix' : 'Both',
                                'method_types' : ['Toxicity Test Procedure', 'Sample Analysis']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(ToxicitySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, ('Matrix', 'Both')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(ToxicitySearchView.result_fields))
                                
    def test_view_method_types_filter(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'all',
                                'media' : 'all',
                                'matrix' : 'all',
                                'method_types' : ['Toxicity Test Procedure']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(ToxicitySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None, None, None])
        self.assertEqual(resp.context['selected_method_types'], ['Toxicity Test Procedure'])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(ToxicitySearchView.result_fields))

    def test_view_no_method_types(self):
        resp = self.client.get(reverse('methods-toxicity'),
                               {'subcategory' : 'all',
                                'media' : 'all',
                                'matrix' : 'all',
                                'method_types' : []})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)

        
class TestPhysicalSearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_analyte_all_vw',
                'method_vw']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-physical'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'physical_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-physical'),
                               {'analyte' : 'all',
                                'method_types' : ['Sample Analysis', 'Sample Collection']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'physical_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(PhysicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 3)
        self.assertEqual(len(resp.context['results'][0]), len(PhysicalSearchView.result_fields))

    def test_view_analyte_filter(self):
        resp = self.client.get(reverse('methods-physical'),
                               {'analyte' : '19011',
                                'method_types' : ['Sample Analysis', 'Sample Collection']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'physical_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(PhysicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Analyte', 'Water level (E-11994)')])
        self.assertEqual(resp.context['selected_method_types'], [])
        self.assertEqual(len(resp.context['results']), 2)
        self.assertEqual(len(resp.context['results'][0]), len(PhysicalSearchView.result_fields))

    def test_view_method_types_filter(self):
        resp = self.client.get(reverse('methods-physical'),
                               {'analyte' : 'all',
                                'method_types' : ['Sample Collection']})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'physical_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(PhysicalSearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['selected_method_types'], ['Sample Collection'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(PhysicalSearchView.result_fields))
        
    def test_view_no_method_types(self):
        resp = self.client.get(reverse('methods-physical'),
                               {'analyte' : 'all',
                                'method_types' : []})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'physical_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)

        

class TestStreamPhysicalSearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_analyte_jn_stg_vw.json']
    
    def test_view(self):
        resp = self.client.get(reverse('methods-stream_physical'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'stream_physical_search.html')
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(StreamPhysicalSearchView.header_abbrev_set))
        self.assertEqual(len(resp.context['results']), 3)
        self.assertEqual(len(resp.context['results'][0]), len(StreamPhysicalSearchView.result_fields))
        
class TestRegulatorySearchView(TestCase):
    fixtures = ['definitions_dom.json',
                'reg_query_vw.json',
                'regulation_ref.json',
                'analyte_code_rel.json']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-regulatory'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'regulatory_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)

    def test_view_no_analyte(self):
        resp = self.client.get(reverse('methods-regulatory'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : '',
                                'regulation' : 'all'})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'regulatory_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('header_defs', resp.context)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('selected_method_types', resp.context)
        self.assertNotIn('results', resp.context)        
        
    def test_view_analyte_name_filter(self):
        resp = self.client.get(reverse('methods-regulatory'),
                               {'analyte_kind' : 'name',
                                'analyte_value' : 'Amenable cyanide',
                                'regulation' : 'all'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'regulatory_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(RegulatorySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['analyte_name'], 'Amenable cyanide')
        self.assertEqual(resp.context['analyte_code'], 'E-10275')
        self.assertItemsEqual(resp.context['syn'], ['Amenable cyanide', 'Cyanide amenable to chlorination', 'Available Cyanide'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(RegulatorySearchView.result_fields))
        self.assertEqual(resp.context['method_count'], 1)
        
    def test_view_analyte_code_filter(self):
        resp = self.client.get(reverse('methods-regulatory'),
                               {'analyte_kind' : 'code',
                                'analyte_value' : 'E-10275',
                                'regulation' : 'all'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'regulatory_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(RegulatorySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [None])
        self.assertEqual(resp.context['analyte_name'], 'Available Cyanide')
        self.assertEqual(resp.context['analyte_code'], 'E-10275')
        self.assertItemsEqual(resp.context['syn'], ['Amenable cyanide', 'Cyanide amenable to chlorination', 'Available Cyanide'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(RegulatorySearchView.result_fields))
        self.assertEqual(resp.context['method_count'], 1)
        
    def test_view_analyte_code_and_regulation_filter(self):
        resp = self.client.get(reverse('methods-regulatory'),
                               {'analyte_kind' : 'code',
                                'analyte_value' : 'E-10275',
                                'regulation' : 'NPDES'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'regulatory_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertEqual(len(resp.context['header_defs']), len(RegulatorySearchView.header_abbrev_set))
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['criteria'], [('Regulation', 'National Pollutant Discharge Elimination System')])
        self.assertEqual(resp.context['analyte_name'], 'Available Cyanide')
        self.assertEqual(resp.context['analyte_code'], 'E-10275')
        self.assertItemsEqual(resp.context['syn'], ['Amenable cyanide', 'Cyanide amenable to chlorination', 'Available Cyanide'])
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]), len(RegulatorySearchView.result_fields))
        self.assertEqual(resp.context['method_count'], 1)
        
  
class TestExportRegulatorySearchView(TestCase):
    fixtures = ['reg_query_vw.json']
    
    def test_view_output_tsv(self):
        resp = self.client.get(reverse('methods-regulatory_export_tsv'),
                               {'analyte_kind' : 'code',
                                'analyte_value' : 'E-10275',
                                'regulation' : 'all'})
        
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'text/tab-separated-values')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=regulatory_search.tsv')
        
    def test_view_output_xls(self):
        resp = self.client.get(reverse('methods-regulatory_export_xls'),
                               {'analyte_kind' : 'code',
                                'analyte_value' : 'E-10275',
                                'regulation' : 'all'})
                               
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'application/vnd.ms-excel')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=regulatory_search.xls')
        
    def test_view_bad_query(self):
        resp = self.client.get(reverse('methods-regulatory_export_xls'))
        self.assertEqual(resp.status_code, 404)      
  
                                
class TestTabularRegulatorySearchView(TestCase):
    fixtures = ['regulatory_method_report.json',
                'analyte_code_rel.json']
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-tabular_reg'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tabular_reg_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('query_string', resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('results', resp.context)
    
    def test_view_no_filter(self):
        resp = self.client.get(reverse('methods-tabular_reg'),
                               {'analyte' : 'all'})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tabular_reg_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(len(resp.context['results']), 7)
        self.assertEqual(len(resp.context['results'][0]['r']), len(TabularRegulatorySearchView.result_fields))
        self.assertIn('analyte_code', resp.context['results'][0])
        self.assertIn('syn', resp.context['results'][0])

    def test_view_analyte_filter(self):
        resp = self.client.get(reverse('methods-tabular_reg'),
                               {'analyte' : 'Available Cyanide'})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tabular_reg_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(len(resp.context['results']), 1)
        self.assertEqual(len(resp.context['results'][0]['r']), len(TabularRegulatorySearchView.result_fields))
        self.assertEqual(resp.context['results'][0]['analyte_code'], 'E-10275')
        self.assertItemsEqual(resp.context['results'][0]['syn'], ['Amenable cyanide', 'Available Cyanide', 'Cyanide amenable to chlorination'])

   
class TestKeywordSearchView(TestCase):
    '''Decided to not test query as it doesn't use the Django ORM. This would require a special test runner
    to do this.
    '''
    
    def test_view_no_query(self):
        resp = self.client.get(reverse('methods-keyword'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'keyword_search.html')
        self.assertNotIn('keyword', resp.context)
        self.assertNotIn('current_url', resp.context)
        self.assertNotIn('results', resp.context)
        self.assertNotIn('error', resp.context)
        
    def test_view_blank_search_field(self):
        resp = self.client.get(reverse('methods-keyword'),
                                       {'keyword_search_field' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'keyword_search.html')
        self.assertNotIn('keyword', resp.context)
        self.assertNotIn('current_url', resp.context)
        self.assertNotIn('results', resp.context)
        self.assertIn('error', resp.context)
       

class TestBrowseMethodsView(TestCase):
    fixtures = ['method_vw.json']
    
    def test_view(self):
        resp = self.client.get(reverse('methods-browse'))
        
        self.assertEqual(resp.status_code, 200);
        self.assertTemplateUsed(resp, 'browse_methods.html')
        self.assertEqual(len(resp.context['object_list']), 16)
        
        
class TestMethodSummaryView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_summary_vw.json']
#I am having trouble dumping the MethodAnalyteVW using the dumpdata command so I'm omiting this for now.                
#                'method_analyte_vw.json',
#                'analyte_code_rel.json']
    
    def test_view_with_valid_id(self):
        resp = self.client.get(reverse('methods-method_summary', kwargs={'method_id' : 4846}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'method_summary.html')
        self.assertIn('data', resp.context)
        self.assertEqual(resp.context['data'].method_id, 4846)
        self.assertIn('field_defs', resp.context)
        self.assertIn('analyte_data', resp.context)
        self.assertIn('notes', resp.context)
        # Add more tests to test analyte_data  and notes contents when method_analyte_vw.json fixture is available.
        
    def test_view_with_invalid_id(self):
        resp = self.client.get(reverse('methods-method_summary', kwargs={'method_id' : 1}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'method_summary.html')
        self.assertIn('data', resp.context)
        self.assertIsNone(resp.context['data'])
        self.assertIn('analyte_data', resp.context)
        self.assertIsNone(resp.context['analyte_data'])
        self.assertNotIn('field_defs', resp.context)
        
        
class TestRegulatoryMethodSummaryView(TestCase):
    fixtures = ['definitions_dom.json',
                'reg_query_vw.json']
#I am having trouble dumping the MethodAnalyteVW using the dumpdata command so I'm omiting this for now.                
#                'method_analyte_vw.json',
#                'analyte_code_rel.json']

    def test_view_with_valid_id(self):
        resp = self.client.get(reverse('methods-method_summary_reg', kwargs={'rev_id' : 14}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'method_summary.html')
        self.assertIn('data', resp.context)
        self.assertEqual(resp.context['data'].revision_id, 14)
        self.assertIn('field_defs', resp.context)
        self.assertIn('analyte_data', resp.context)
        self.assertIn('notes', resp.context)
        # Add more tests to test analyte_data  and notes contents when method_analyte_vw.json fixture is available.
        
    def test_view_with_invalid_id(self):
        resp = self.client.get(reverse('methods-method_summary_reg', kwargs = {'rev_id' : 1565}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'method_summary.html')
        self.assertIn('data', resp.context)
        self.assertIsNone(resp.context['data'])
        self.assertIn('analyte_data', resp.context)
        self.assertIsNone(resp.context['analyte_data'])
        self.assertNotIn('field_defs', resp.context)
        
class TestBiologicalMethodSummaryView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_summary_vw.json']
#I am having trouble dumping the MethodAnalyteVW using the dumpdata command so I'm omiting this for now.                
#                'method_analyte_vw.json',
#                'analyte_code_rel.json']

    def test_view_with_valid_id(self):
        resp = self.client.get(reverse('methods-biological_method_summary', kwargs={'method_id' : 4845}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertEqual(resp.context['data'].method_id, 4845)
        self.assertIn('field_defs', resp.context)
        self.assertIn('analyte_data', resp.context)  
        
    def test_view_with_invalid_id(self):
        resp = self.client.get(reverse('methods-biological_method_summary', kwargs={'method_id' : 1}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'biological_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertIsNone(resp.context['data'])
        self.assertIn('analyte_data', resp.context)
        self.assertIsNone(resp.context['analyte_data'])
        self.assertNotIn('field_defs', resp.context)      

class TestToxicityMethodSummaryView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_summary_vw.json']
#I am having trouble dumping the MethodAnalyteVW using the dumpdata command so I'm omiting this for now.                
#                'method_analyte_vw.json',
#                'analyte_code_rel.json']

    def test_view_with_valid_id(self):
        resp = self.client.get(reverse('methods-toxicity_method_summary', kwargs={'method_id' : 4845}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertEqual(resp.context['data'].method_id, 4845)
        self.assertIn('field_defs', resp.context)
        self.assertIn('analyte_data', resp.context)  
        
    def test_view_with_invalid_id(self):
        resp = self.client.get(reverse('methods-toxicity_method_summary', kwargs={'method_id' : 1}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertIsNone(resp.context['data'])
        self.assertIn('analyte_data', resp.context)
        self.assertIsNone(resp.context['analyte_data'])
        self.assertNotIn('field_defs', resp.context)      
           

class TestStreamPhysicalMethodSummaryView(TestCase):
    fixtures = ['definitions_dom.json',
                'method_stg_summary_vw.json']


    def test_view_with_valid_id(self):
        resp = self.client.get(reverse('methods-stream_physical_method_summary', kwargs={'method_id' : 4830}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'stream_physical_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertEqual(resp.context['data'].method_id, 4830)
        self.assertIn('field_defs', resp.context)
        self.assertIn('analyte_data', resp.context)
        self.assertEqual(len(resp.context['analyte_data']), 0)  
        
    def test_view_with_invalid_id(self):
        resp = self.client.get(reverse('methods-toxicity_method_summary', kwargs={'method_id' : 1}))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'toxicity_method_summary.html')
        self.assertIn('data', resp.context)
        self.assertIsNone(resp.context['data'])
        self.assertIn('analyte_data', resp.context)
        self.assertIsNone(resp.context['analyte_data'])
        self.assertNotIn('field_defs', resp.context)  
        
            
class TestExportMethodAnalyte(TestCase): 
    # Add fixtures when when download MethodAnalyteVw data and create a fixture
    
    def test_view(self):
        resp = self.client.get(reverse('methods-method_analyte_export', kwargs={'method_id' : 1})) 
        self.assertEqual(resp.status_code, 200) 
        self.assertEqual(resp['Content-Type'], 'text/tab-separated-values')
        self.assertEqual(resp['Content-Disposition'], 'attachment; filename=1_analytes.tsv')  
        
