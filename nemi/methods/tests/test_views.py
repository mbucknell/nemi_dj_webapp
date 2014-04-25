'''
Created on Mar 13, 2012

@author: mbucknel
'''

from django.test import SimpleTestCase, TestCase

from factory.django import DjangoModelFactory
from rest_framework.test import APIRequestFactory

from methods.views import _clean_name, _clean_keyword, MethodRestViewSet

class CleanNameTestCase(SimpleTestCase):

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


class CleanKeywordTestCase(SimpleTestCase):

    def test_with_no_special_characters(self):
        keyword = 'nitrate'
        self.assertEqual(_clean_keyword(keyword), '%nitrate%')

    def test_with_quote(self):
        keyword = "ni'trate"
        self.assertEqual(_clean_keyword(keyword), "%ni''trate%")

    def test_with_two_quotes(self):
        keyword = "ni'trate'chloride"
        self.assertEqual(_clean_keyword(keyword), "%ni''trate''chloride%")

    def test_with_double_quotes(self):
        keyword = 'ni"trate'
        self.assertEqual(_clean_keyword(keyword), '%ni""trate%')

    def test_with_two_double_quotes(self):
        keyword = 'ni"trate"chloride'
        self.assertEqual(_clean_keyword(keyword), '%ni""trate""chloride%')

    def test_with_percent(self):
        keyword = 'ni%trate'
        self.assertEqual(_clean_keyword(keyword), '%ni\%trate%')

    def test_with_two_percents(self):
        keyword = 'ni%trate%chloride'
        self.assertEqual(_clean_keyword(keyword), '%ni\%trate\%chloride%')

    def test_with_percent_and_quote_chars(self):
        keyword = 'ni"tr%ate'
        self.assertEqual(_clean_keyword(keyword), '%ni""tr\%ate%')

    def test_with_dash(self):
        keyword = 'ni-trate'
        self.assertEqual(_clean_keyword(keyword), '%ni\-trate%')

    def test_with_plus_sign(self):
        keyword = 'ni+trate'
        self.assertEqual(_clean_keyword(keyword), '%ni\+trate%')

    def test_with_comma_and_quote(self):
        keyword = "ni,tr'ate"
        self.assertEqual(_clean_keyword(keyword), "%ni\,tr''ate%")


class MethodSummaryFactory(DjangoModelFactory):
    FACTORY_FOR = 'methods.MethodVW'

    source_method_identifier = 'A'
    method_descriptive_name = 'name'
    method_official_name = 'official_name',
    method_source_id = '1234'
    sam_complexity = 'A'
    source_citation_id = ' 88'
    brief_method_summary = 'A'
    media_name = 'book'
    instrumentation_id = 1
    method_source = 'USGS'
    method_source_name = 'US Geological Survey'
    method_subcategory_id = '1'
    source_citation = 'A'
    instrumentation = 'AA'
    instrumentation_description = 'what'
    regs_only = 'n'
    method_type_id = 1
    publication_year = '1991'
    author = 'A'


class MethodSummaryRestViewSetTestCase(TestCase):

    def setUp(self):
        self.m1 = MethodSummaryFactory(method_id=1, method_category='A', method_subcategory='A1')
        self.m2 = MethodSummaryFactory(method_id=2, method_category='A', method_subcategory='A1')
        self.m3 = MethodSummaryFactory(method_id=3, method_category='A', method_subcategory='A2')
        self.m4 = MethodSummaryFactory(method_id=4, method_category='A', method_subcategory='A3')
        self.m5 = MethodSummaryFactory(method_id=5, method_category='B', method_subcategory='B1')
        self.m6 = MethodSummaryFactory(method_id=6, method_category='C', method_subcategory='C1')
        self.m7 = MethodSummaryFactory(method_id=7, method_category='C', method_subcategory='A2')
        self.m8 = MethodSummaryFactory(method_id=8, method_category='C', method_subcategory='C2')

        self.test_view = MethodRestViewSet()
        self.factory = APIRequestFactory()

    def test_get_queryset_no_query_parameters(self):
        self.test_view.request = self.factory.get('/api/methods/')
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 8)

    def test_get_queryset_category_parameters(self):
        self.test_view.request = self.factory.get('/api/methods/', {'method_category' : 'A'})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 4)
        self.assertIsNotNone(result.get(method_id=1))
        self.assertIsNotNone(result.get(method_id=2))
        self.assertIsNotNone(result.get(method_id=3))
        self.assertIsNotNone(result.get(method_id=4))

    def test_get_queryset_multiple_category_parameters(self):
        self.test_view.request = self.factory.get('/api/methods/', {'method_category' : ['A', 'B']})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 5)
        self.assertIsNotNone(result.get(method_id=1))
        self.assertIsNotNone(result.get(method_id=2))
        self.assertIsNotNone(result.get(method_id=3))
        self.assertIsNotNone(result.get(method_id=4))
        self.assertIsNotNone(result.get(method_id=5))


    def test_get_queryset_subcategory_parameters(self):
        self.test_view.request = self.factory.get('/api/methods', {'method_subcategory' : 'A2'})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 2)
        self.assertIsNotNone(result.get(method_id=3))
        self.assertIsNotNone(result.get(method_id=7))

    def test_get_queryset_multiple_subcategory_parameters(self):
        self.test_view.request = self.factory.get('/api/methods', {'method_subcategory' : ['A2', 'B1']})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 3)
        self.assertIsNotNone(result.get(method_id=3))
        self.assertIsNotNone(result.get(method_id=5))
        self.assertIsNotNone(result.get(method_id=7))

    def test_get_queryset_category_and_subcategory_parameters(self):
        self.test_view.request = self.factory.get('/api/methods', {'method_category' : 'A', 'method_subcategory' : 'A2'})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 1)
        self.assertIsNotNone(result.get(method_id=3))

    def test_get_queryset_none_exists_parameters(self):
        self.test_view.request = self.factory.get('/api/methods', {'method_category' : 'B', 'method_subcategory' : 'A2'})
        result = self.test_view.get_queryset()

        self.assertEqual(result.count(), 0)
