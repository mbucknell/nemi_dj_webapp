'''
Created on Jul 26, 2012

@author: mbucknel
'''

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from common.utils.forms import get_criteria_from_field_data

# TODO: Need to add more tests for the statistical methods views        
class TestAddStatisticalSourceView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', '', password='test')
        self.user1.is_staff = True
        self.user1.is_active = True
        self.user1.save()
        
        
    def test_view_get(self):
        resp = self.client.get(reverse('sams-create_method')) 
        
        self.assertRedirects(resp, '/accounts/login/?next=%s' % (reverse('sams-create_method')))
        
        self.client.login(username='user1', password='test')
        resp = self.client.get(reverse('sams-create_method'))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'create_statistic_source.html')
        self.assertIn('form', resp.context)
        
                                 
class TestStatisticSearchViewNoMethods(TestCase):
    fixtures = ['static_data.json']  
      
    def test_view_no_query(self):
        resp = self.client.get(reverse('sams-statistics'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html')
        self.assertIn('search_form', resp.context)
        self.assertEqual(resp.context['hide_search'], False)
        self.assertEqual(resp.context['show_results'], False)
        self.assertNotIn('query_string',resp.context)
        self.assertNotIn('header_defs',resp.context)
        self.assertNotIn('criteria', resp.context)
        self.assertNotIn('results', resp.context)
        
    def test_view_query_all(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                              'complexity' : 'all', 
                                                              'analysis_types' : '',
                                                              'publication_source_type' : '',
                                                              'design_objectives' : '',
                                                              'media_emphasized' : '',
                                                              'special_topics' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, None, None, None, None, None])
        self.assertQuerysetEqual(resp.context['results'], [])
        
class TestStatisticSearchView(TestCase):
    
    fixtures = ['source_citation_ref.json']

    def test_filter_query(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : 3, 
                                                              'complexity' : 'all', 
                                                              'analysis_types' : '',
                                                              'publication_source_type' : '',
                                                              'design_objectives' : '',
                                                              'media_emphasized' : '',
                                                              'special_topics' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['criteria'],  [None, get_criteria_from_field_data(resp.context['search_form'], 'item_type'), None, None, None, None, None])
        self.assertEqual(resp.context['results'].count(), 4);
        