'''
Created on Jul 26, 2012

@author: mbucknel
'''

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.test import TestCase

from common.models import SourceCitationRef, PublicationSourceRel, SourceCitationOnlineRef, PublicationSourceRelStg
from common.models import Method, StatAnalysisRel, StatDesignRel, StatMediaRel, StatTopicRel, StatisticalItemType, MethodSubcategoryRef
from common.models import StatAnalysisRelStg, StatDesignRelStg, StatMediaRelStg, StatTopicRelStg
from common.models import MethodTypeRef, InstrumentationRef, StatisticalAnalysisType, StatisticalDesignObjective, StatisticalTopics, MediaNameDOM
from common.models import MethodSourceRef, StatisticalSourceType, MethodOnline

# TODO: Need to add more functional tests for the statistical update, update lists, and submission/approval views. 
# Could also improve TestAddStatMethodOnlineView      
class TestAddStatMethodOnlineView(TestCase):
    
    fixtures = ['static_data.json', 
                'method_subcategory_ref.json', 
                'method_type_ref.json',
                'method_source_ref.json',
                'instrumentation_ref.json']
    
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
        self.assertIn('action_url', resp.context)
        self.assertEqual(resp.context['action_url'], reverse('sams-create_method'))
        
        self.client.logout()
        
    def test_view_post_with_error(self):
        self.client.login(username='user1', password='test')
        
        resp = self.client.post(reverse('sams-create_method'),
                                {'source_method_identifier' : 'SAMS M1'})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'create_statistic_source.html')
        self.assertIn('form', resp.context)
        self.assertIn('action_url', resp.context)
        self.assertEqual(resp.context['action_url'], reverse('sams-create_method'))
        self.assertNotEqual(len(resp.context['form'].errors), 0)

        self.client.logout()
        
    def test_view_post(self):
        self.client.login(username='user1', password='test')
        
        resp = self.client.post(reverse('sams-create_method'),
                                {'source_method_identifier' : 'SAMS M1',
                                 'method_official_name' : 'SAMs Method One',
                                 'method_source' : 16,
                                 'author' : 'A. B. Smith',
                                 'brief_method_summary' : 'SAMS 1 Brief Method Summary',
                                 'publication_year' : 2012,
                                 'source_citation_name' : 'SAMS-M1',
                                 'item_type' : 3,
                                 'sponser_types' : 1,
                                 'analysis_types' : 1,
                                 'design_objectives' : (13, 10),
                                 'sam_complexity' : 'Low',
                                 'level_of_training' : 'Basic',
                                 'media_emphasized' : 'OTHER'
                                 })
        q1 = MethodOnline.objects.filter(source_method_identifier='SAMS M1')
        s1 = SourceCitationOnlineRef.objects.filter(source_citation_id=q1[0].source_citation_id)
        
        self.assertEqual(len(q1), 1)
        self.assertEqual(len(s1), 1)
        
        self.assertEqual(len(PublicationSourceRelStg.objects.filter(source_citation_ref_id=q1[0].source_citation_id)), 1)
        self.assertEqual(len(StatAnalysisRelStg.objects.filter(method_id=q1[0].method_id)), 1)
        self.assertEqual(len(StatDesignRelStg.objects.filter(method_id=q1[0].method_id)), 2)
        self.assertEqual(len(StatMediaRelStg.objects.filter(method_id=q1[0].method_id)), 1)
        self.assertEqual(len(StatTopicRelStg.objects.filter(method_id=q1[0].method_id)), 0)
        self.assertRedirects(resp, '/sams/method_detail/%s/' % q1[0].method_id)

        self.client.logout()
                                 
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
    
    fixtures = ['static_data.json', 
                'method_subcategory_ref.json', 
                'method_type_ref.json',
                'method_source_ref.json',
                'instrumentation_ref.json']
    
    def setUp(self):
        self.sc1 = SourceCitationRef.objects.create(source_citation_id=1,
                                                    source_citation='SAMS M1',
                                                    title='Official name 1',
                                                    country='USA',
                                                    author='A. B. Smith',
                                                    publication_year='2012',
                                                    source_citation_name='Statistical Method One',
                                                    item_type=StatisticalItemType.objects.get(item='Book')
                                                    )
        self.s1_sponser_types = PublicationSourceRel.objects.create(source_citation_ref=self.sc1, source=StatisticalSourceType.objects.get(stat_source_index=6))
        
        self.sc2 = SourceCitationRef.objects.create(source_citation_id=2,
                                                    source_citation='SAMS M2',
                                                    title='Official name 2',
                                                    country='USA',
                                                    author='A. B. Jones',
                                                    publication_year='2012',
                                                    source_citation_name='Statistical Method Two',
                                                    item_type=StatisticalItemType.objects.get(item='Book')
                                                    )
        self.s2_sponser_types = PublicationSourceRel.objects.create(source_citation_ref=self.sc1, source=StatisticalSourceType.objects.get(stat_source_index=6))
        
        self.sc3 = SourceCitationRef.objects.create(source_citation_id=3,
                                                    source_citation='SAMS M3',
                                                    title='Official name 3',
                                                    country='USA',
                                                    author='G. H. Wang',
                                                    publication_year='2012',
                                                    source_citation_name='Statistical Method Three',
                                                    item_type=StatisticalItemType.objects.get(item='Website')
                                                    )
        self.s2_sponser_types = PublicationSourceRel.objects.create(source_citation_ref=self.sc1, source=StatisticalSourceType.objects.get(stat_source_index=8))
        
        self.m1 = Method.objects.create(method_id=1,
                                        method_subcategory=MethodSubcategoryRef.objects.get(method_subcategory_id=16),
                                        source_citation=self.sc1,
                                        method_type=MethodTypeRef.objects.get(method_type_id=3),
                                        instrumentation=InstrumentationRef.objects.get(instrumentation='NA'),
                                        method_source=MethodSourceRef.objects.get(pk=102),
                                        source_method_identifier='SAMS M1',
                                        method_descriptive_name='Statistical Method One',
                                        method_official_name='Official name 1',
                                        sam_complexity='Low',
                                        level_of_training='Advanced',
                                        )
        self.m1_analysis = StatAnalysisRel.objects.create(method=self.m1, analysis_type=StatisticalAnalysisType.objects.get(stat_analysis_index=1))
        self.m1_design = StatDesignRel.objects.create(method=self.m1, design_objective=StatisticalDesignObjective.objects.get(stat_design_index=11))
        self.m1_media = StatMediaRel.objects.create(method=self.m1, media_name=MediaNameDOM.objects.get(media_name='AIR'))
        self.m1_topic = StatTopicRel.objects.create(method=self.m1, topic=StatisticalTopics.objects.get(stat_topic_index=2))
        
        self.m2 = Method.objects.create(method_id=2,
                                        method_subcategory=MethodSubcategoryRef.objects.get(method_subcategory_id=16),
                                        source_citation=self.sc2,
                                        method_type=MethodTypeRef.objects.get(method_type_id=3),
                                        instrumentation=InstrumentationRef.objects.get(instrumentation='NA'),
                                        method_source=MethodSourceRef.objects.get(pk=102),
                                        source_method_identifier='SAMS M2',
                                        method_descriptive_name='Statistical Method Two',
                                        method_official_name='Official name 2',
                                        sam_complexity='Medium',
                                        level_of_training='Intermediate'
                                        )
        self.m2_analysis = StatAnalysisRel.objects.create(method=self.m2, analysis_type=StatisticalAnalysisType.objects.get(stat_analysis_index=1))
        self.m2_design = StatDesignRel.objects.create(method=self.m2, design_objective=StatisticalDesignObjective.objects.get(stat_design_index=10))
        self.m2_media = StatMediaRel.objects.create(method=self.m2, media_name=MediaNameDOM.objects.get(media_name='AIR'))
        self.m2_topic = StatTopicRel.objects.create(method=self.m2, topic=StatisticalTopics.objects.get(stat_topic_index=3))
        
        self.m3 = Method.objects.create(method_id=3,
                                        method_subcategory=MethodSubcategoryRef.objects.get(method_subcategory_id=16),
                                        source_citation=self.sc3,
                                        method_type=MethodTypeRef.objects.get(method_type_id=3),
                                        instrumentation=InstrumentationRef.objects.get(instrumentation='NA'),
                                        method_source=MethodSourceRef.objects.get(pk=102),
                                        source_method_identifier='SAMS M3',
                                        method_descriptive_name='Statistical Method Three',
                                        method_official_name='Official name 3',
                                        sam_complexity='Low',
                                        level_of_training='Intermediate'
                                        )
        self.m3_analysis = StatAnalysisRel.objects.create(method=self.m3, analysis_type=StatisticalAnalysisType.objects.get(stat_analysis_index=2))
        self.m3_design = StatDesignRel.objects.create(method=self.m3, design_objective=StatisticalDesignObjective.objects.get(stat_design_index=11))
        self.m3_media = StatMediaRel.objects.create(method=self.m3, media_name=MediaNameDOM.objects.get(media_name='OTHER'))
        self.m3_topic = StatTopicRel.objects.create(method=self.m3, topic=StatisticalTopics.objects.get(stat_topic_index=2))
        
    def test_post(self):
        resp = self.client.post(reverse('sams-statistics'))
        self.assertEqual(resp.status_code, 405)

    def test_filter_by_item_type(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : 3, 
                                                            'complexity' : 'all', 
                                                            'analysis_types' : '',
                                                            'publication_source_type' : '',
                                                            'study_objectives' : '',
                                                            'media_emphasized' : '',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, ('Item type', StatisticalItemType.objects.get(item='Book')), None, None, None, None, None])
        self.assertEqual(len(resp.context['results']), 2)
        
    def test_filter_by_complexity(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'Low', 
                                                            'analysis_type' : '',
                                                            'publication_source_type' : '',
                                                            'study_objective' : '',
                                                            'media_emphasized' : '',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, ('Complexity', 'Low'), None, None, None, None])
        self.assertEqual(len(resp.context['results']), 2)
        
    def test_filter_by_analysis_type(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'all', 
                                                            'analysis_type' : 2,
                                                            'publication_source_type' : '',
                                                            'study_objective' : '',
                                                            'media_emphasized' : '',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, None, ('Analysis type', StatisticalAnalysisType.objects.get(stat_analysis_index=2)), None, None, None])
        self.assertEqual(len(resp.context['results']), 1)
        
    def test_filter_by_publication_source_type(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'all', 
                                                            'analysis_type' : '',
                                                            'publication_source_type' : 8,
                                                            'study_objective' : '',
                                                            'media_emphasized' : '',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, None, None, ('Publication source type', StatisticalSourceType.objects.get(stat_source_index=8)), None, None])
        self.assertEqual(len(resp.context['results']), 1)
        
    def test_filter_by_study_objective(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'all', 
                                                            'analysis_type' : '',
                                                            'publication_source_type' : '',
                                                            'study_objective' : 11,
                                                            'media_emphasized' : '',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [('What you are interested in', StatisticalDesignObjective.objects.get(stat_design_index=11)), None, None, None, None, None, None])
        self.assertEqual(len(resp.context['results']), 2)
        
    def test_filter_by_media_emphasized(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'all', 
                                                            'analysis_type' : '',
                                                            'publication_source_type' : '',
                                                            'study_objective' : '',
                                                            'media_emphasized' : 'AIR',
                                                            'special_topic' : ''})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, None, None, None, ('Media emphasized', MediaNameDOM.objects.get(media_name='AIR')), None])
        self.assertEqual(len(resp.context['results']), 2)
        
    def test_filter_by_special_topic(self):
        resp = self.client.get(reverse('sams-statistics'), {'item_type' : '', 
                                                            'complexity' : 'all', 
                                                            'analysis_type' : '',
                                                            'publication_source_type' : '',
                                                            'study_objective' : '',
                                                            'media_emphasized' : '',
                                                            'special_topic' : 3})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statistic_search.html');
        self.assertIn('search_form',resp.context)
        self.assertEqual(resp.context['hide_search'], True)
        self.assertEqual(resp.context['show_results'], True)
        self.assertIn('query_string', resp.context)
        self.assertEqual(resp.context['header_defs'], None)
        self.assertEqual(resp.context['criteria'], [None, None, None, None, None, None, ('Special topic', StatisticalTopics.objects.get(stat_topic_index=3))])
        self.assertEqual(len(resp.context['results']), 1)
        
class TestSubmitForReviewView(TestCase):
     
    def test_permissions(self):
        url = reverse('sams-submit_for_review', kwargs={'pk' : '1'})
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        
        self.client.logout()
        
class TestUpdateStatisticalMethodOnlineView(TestCase):
    def test_permission(self):
        url = reverse('sams-update_method', kwargs={'pk' : '1'})
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        
        self.client.logout()
        
    
class TestStatisticalMethodOnlineDetailView(TestCase):
    
    def test_permission(self):
        url = reverse('sams-method_detail', kwargs={'pk' : '1'})
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        
        self.client.logout()

class TestUpdateStatisticalMethodOnlineListView(TestCase):

    def test_permission(self):
        url = reverse('sams-update_method_list')
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        self.client.logout()
        
        
class TestApproveStatMethod(TestCase):
    
    def setUp(self):
        self.g1 = Group.objects.create(name='nemi_admin')
        self.user1 = User.objects.create_user('user1', '', password='test')
            
    def test_permissions(self):
        url = reverse('sams-approve_method', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/sams/not_allowed/?next=%s' % url)
        
        self.user1.groups.add(self.g1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
                
        self.client.logout()
    
class TestReviewStatMethodStgListView(TestCase):
    
    def setUp(self):
        self.g1 = Group.objects.create(name='nemi_admin')
        self.user1 = User.objects.create_user('user1', '', password='test')
            
    def test_permissions(self):
        url = reverse('sams-method_review_list')
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/sams/not_allowed/?next=%s' % url)
        
        self.user1.groups.add(self.g1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
                
        self.client.logout()
 
class TestStatisticalMethodStgDetailView(TestCase):
    
    def setUp(self):
        self.g1 = Group.objects.create(name='nemi_admin')
        self.user1 = User.objects.create_user('user1', '', password='test')
            
    def test_permissions(self):
        url = reverse('sams-method_detail_for_approval', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/sams/not_allowed/?next=%s' % url)
        
        self.user1.groups.add(self.g1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
                
        self.client.logout()
 
class TestUpdateStatisticalMethodStgView(TestCase):
    def setUp(self):
        self.g1 = Group.objects.create(name='nemi_admin')
        self.user1 = User.objects.create_user('user1', '', password='test')
            
    def test_permissions(self):
        url = reverse('sams-update_review_method', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')
        
        resp = self.client.get(url)
        self.assertRedirects(resp, '/sams/not_allowed/?next=%s' % url)
        
        self.user1.groups.add(self.g1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
                
        self.client.logout()
                            