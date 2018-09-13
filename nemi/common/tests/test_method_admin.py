from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from common import models


class TestMethodAdminPermissions(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users for each role - admin, data entry, and reviewer.
        self.users = {
            'admin': User.objects.create(username='method_admin', is_superuser=True),
            'reviewer': User.objects.create(username='method_reviewer'),
            'data_entry_1': User.objects.create(username='method_data_entry_1'),
            'data_entry_2': User.objects.create(username='method_data_entry_2'),
        }
        self.groups = {
            'admin': Group.objects.get_or_create(name='method_admin')[0],
            'reviewer': Group.objects.get_or_create(name='method_reviewer')[0],
            'data_entry': Group.objects.get_or_create(name='method_data_entry')[0]
        }
        self.users['admin'].groups.add(self.groups['admin'])
        self.users['reviewer'].groups.add(self.groups['reviewer'])
        self.users['data_entry_1'].groups.add(self.groups['data_entry'])
        self.users['data_entry_2'].groups.add(self.groups['admin'])

        # Create dummy methods in each stage, inserted by a `data_entry` user.
        instrumentation = models.InstrumentationRef.objects.create(
            instrumentation_id=1,
            instrumentation='instrumentation',
            instrumentation_description='description'
        )
        method_type = models.MethodTypeRef.objects.create(
            method_type_id=1,
            method_type_desc='method_type_desc'
        )
        method_fields = {
            'source_citation_id': 1,
            'method_official_name': 'name1',
            'brief_method_summary': 'summary1',
            'method_type': method_type,
            'instrumentation': instrumentation
        }

        self.methods = {
            'online_1': models.MethodOnline.objects.create(
                method_id=1,
                source_method_identifier='id1',
                reviewer_name=self.users['reviewer'].username,
                insert_person_name=self.users['data_entry_1'].username,
                **method_fields),
            'online_2': models.MethodOnline.objects.create(
                method_id=2,
                source_method_identifier='id2',
                insert_person_name=self.users['data_entry_2'].username,
                **method_fields),
            'stg_1': models.MethodStg.objects.create(
                method_id=1,
                source_method_identifier='id1',
                reviewer_name=self.users['reviewer'].username,
                insert_person_name=self.users['data_entry_1'].username,
                date_loaded=datetime.now(),
                **method_fields),
            'stg_2': models.MethodStg.objects.create(
                method_id=2,
                source_method_identifier='id2',
                insert_person_name=self.users['data_entry_2'].username,
                date_loaded=datetime.now(),
                **method_fields),
            'pub': models.Method.objects.create(
                method_id=1,
                source_method_identifier='id1',
                insert_person_name=self.users['data_entry_1'].username,
                **method_fields)
        }

    def _get(self, url_name, success, args=None):
        response = self.client.get(reverse(url_name, args=args))
        if success:
            self.assertEqual(response.status_code, 200)
        else:
            self.assertNotEqual(response.status_code, 200)
        return response

    def test_admin_user_permissions(self):
        self.client.force_login(self.users['admin'])

        # Method table - published methods
        pk = self.methods['pub'].pk
        self._get('method_admin:common_method_add', False)
        self._get('method_admin:common_method_delete', True, args=[pk])
        # This GET is READ-only. Confirm by checking for string.
        response = self._get('method_admin:common_method_change',
                             True, args=[pk])
        self.assertNotContains(response, 'Save and continue editing')

        # MethodStg table - in-review methods.
        # Admin may publish all in-review methods.
        pk = self.methods['stg_1'].pk
        pk2 = self.methods['stg_2'].pk
        self._get('method_admin:common_methodstg_add', True)
        response = self._get('method_admin:common_methodstg_change', True, args=[pk])
        self._get('method_admin:common_methodstg_delete', True, args=[pk])
        # These GETs should support editing:
        self.assertContains(response, 'Save and continue editing')
        response = self._get('method_admin:common_methodstg_change', True, args=[pk2])
        self.assertContains(response, 'Save and continue editing')

        # MethodOnline table - admin may create and edit methods
        pk = self.methods['online_1'].pk
        pk2 = self.methods['online_2'].pk
        self._get('method_admin:common_methodonline_add', True)
        self._get('method_admin:common_methodonline_delete', True, args=[pk])
        response = self._get('method_admin:common_methodonline_change', True, args=[pk])
        self.assertContains(response, 'Save and continue editing')
        response = self._get('method_admin:common_methodonline_change', True, args=[pk2])
        self.assertContains(response, 'Save and continue editing')

    def _test_no_access(self, user):
        pk = self.methods['pub'].pk
        self.client.force_login(user)

        self._get('method_admin:common_method_add', False)
        self._get('method_admin:common_method_delete', False, args=[pk])
        self._get('method_admin:common_method_change', False, args=[pk])

        self._get('method_admin:common_methodstg_add', False)
        self._get('method_admin:common_methodstg_delete', False, args=[pk])
        self._get('method_admin:common_methodstg_change', False, args=[pk])

        self._get('method_admin:common_methodonline_add', False)
        self._get('method_admin:common_methodonline_delete', False, args=[pk])
        self._get('method_admin:common_methodonline_change', False, args=[pk])

    def test_non_admins(self):
        self._test_no_access(self.users['reviewer'])
        self._test_no_access(self.users['data_entry_1'])

    #
    # Group permissions will be revisited later. These are proper tests, but
    # not currently supported.
    #

    # def test_data_entry_user_permissions(self):
    #     self.client.force_login(self.users['data_entry_1'])

    #     # Method table - published methods
    #     pk = self.methods['pub'].pk
    #     self._get('method_admin:common_method_add', False)
    #     self._get('method_admin:common_method_change', False, args=[pk])
    #     self._get('method_admin:common_method_delete', False, args=[pk])

    #     # MethodStg table - in-review methods
    #     pk = self.methods['stg_1'].pk
    #     pk2 = self.methods['stg_2'].pk
    #     self._get('method_admin:common_methodstg_add', False)
    #     self._get('method_admin:common_methodstg_change', False, args=[pk])
    #     self._get('method_admin:common_methodstg_change', False, args=[pk2])
    #     self._get('method_admin:common_methodstg_delete', False, args=[pk])

    #     # MethodOnline table - user may create and edit own methods
    #     pk = self.methods['online_1'].pk
    #     pk2 = self.methods['online_2'].pk
    #     self._get('method_admin:common_methodonline_add', True)
    #     self._get('method_admin:common_methodonline_change', True, args=[pk])
    #     self._get('method_admin:common_methodonline_change', False, args=[pk2])
    #     self._get('method_admin:common_methodonline_delete', False, args=[pk])

    # def test_reviewer_user_permissions(self):
    #     self.client.force_login(self.users['reviewer'])

    #     # Method table - published methods
    #     pk = self.methods['pub'].pk
    #     self._get('method_admin:common_method_add', False)
    #     self._get('method_admin:common_method_change', False, args=[pk])
    #     self._get('method_admin:common_method_delete', False, args=[pk])

    #     # MethodStg table - in-review methods.
    #     # Reviewer may publish those that they are listed as the reviewer on.
    #     pk = self.methods['stg_1'].pk
    #     pk2 = self.methods['stg_2'].pk
    #     self._get('method_admin:common_methodstg_add', False)
    #     self._get('method_admin:common_methodstg_change', False, args=[pk])
    #     self._get('method_admin:common_methodstg_change', False, args=[pk2])
    #     self._get('method_admin:common_methodstg_delete', False, args=[pk])

    #     # MethodOnline table - reviewer may create and edit own methods
    #     pk = self.methods['online_1'].pk
    #     pk2 = self.methods['online_2'].pk
    #     self._get('method_admin:common_methodonline_add', True)
    #     self._get('method_admin:common_methodonline_change', False, args=[pk])
    #     self._get('method_admin:common_methodonline_change', False, args=[pk2])
    #     self._get('method_admin:common_methodonline_delete', False, args=[pk])
