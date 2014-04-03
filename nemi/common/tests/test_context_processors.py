from django.http import HttpRequest
from django.test import SimpleTestCase
from django.test.utils import override_settings

from ..context_processors import project_settings

class ProjectSettingsTestCase(SimpleTestCase):
    
    @override_settings(GA_TRACKING_CODE='TEST_CODE')
    def test_project_settings(self):
        result = project_settings(HttpRequest())
        self.assertEqual(len(result), 1)
        self.assertEqual(result['settings']['GA_TRACKING_CODE'], 'TEST_CODE')
