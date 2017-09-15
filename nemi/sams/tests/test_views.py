'''
Created on Jul 26, 2012

@author: mbucknel
'''

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from common.models import SourceCitationOnlineRef, PublicationSourceRelStg, MethodOnline
from common.models import StatAnalysisRelStg, StatDesignRelStg, StatMediaRelStg, StatTopicRelStg


# TODO: Need to add more functional tests for the statistical update, update lists, and submission/approval views.
# Could also improve TestAddStatMethodOnlineView
class AddStatMethodOnlineViewTestCase(TestCase):

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
        self.assertTemplateUsed(resp, 'sams/create_statistic_source.html')
        self.assertIn('form', resp.context)
        self.assertIn('action_url', resp.context)
        self.assertEqual(resp.context['action_url'], reverse('sams-create_method'))

        self.client.logout()

    def test_view_post_with_error(self):
        self.client.login(username='user1', password='test')

        resp = self.client.post(reverse('sams-create_method'),
                                {'sam_source_method_identifier' : 'SAMS M1'})

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'sams/create_statistic_source.html')
        self.assertIn('form', resp.context)
        self.assertIn('action_url', resp.context)
        self.assertEqual(resp.context['action_url'], reverse('sams-create_method'))
        self.assertNotEqual(len(resp.context['form'].errors), 0)

        self.client.logout()

    def test_view_post(self):
        self.client.login(username='user1', password='test')

        resp = self.client.post(reverse('sams-create_method'),
                                {'sam_source_method_identifier' : 'SAMS M1',
                                 'sam_method_official_name' : 'SAMs Method One',
                                 'sam_method_source' : 16,
                                 'author' : 'A. B. Smith',
                                 'sam_brief_method_summary' : 'SAMS 1 Brief Method Summary',
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


class SubmitForReviewViewTestCase(TestCase):

    def test_permissions(self):
        url = reverse('sams-submit_for_review', kwargs={'pk' : '1'})

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()

class UpdateStatisticalMethodOnlineViewTestCase(TestCase):

    def test_permission(self):
        url = reverse('sams-update_method', kwargs={'pk' : '1'})

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()


class StatisticalMethodOnlineDetailViewTestCase(TestCase):

    def test_permission(self):
        url = reverse('sams-method_detail', kwargs={'pk' : '1'})

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()

class UpdateStatisticalMethodOnlineListViewTestCase(TestCase):

    def test_permission(self):
        url = reverse('sams-update_method_list')

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1 = User.objects.create_user('user1', '', password='test')
        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.client.logout()


class ApproveStatMethodTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', '', password='test')

    def test_permissions(self):
        url = reverse('sams-approve_method', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1.is_staff = True
        User.save(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()

class ReviewStatMethodStgListViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', '', password='test')

    def test_permissions(self):
        url = reverse('sams-method_review_list')
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1.is_staff = True
        User.save(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        self.client.logout()

class StatisticalMethodStgDetailViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', '', password='test')

    def test_permissions(self):
        url = reverse('sams-method_detail_for_approval', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1.is_staff = True
        User.save(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()


class UpdateStatisticalMethodStgViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('user1', '', password='test')

    def test_permissions(self):
        url = reverse('sams-update_review_method', kwargs={'pk' : '1'})
        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.client.login(username='user1', password='test')

        resp = self.client.get(url)
        self.assertRedirects(resp, '/accounts/login/?next=%s' % url)

        self.user1.is_staff = True
        User.save(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()
