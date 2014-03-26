from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase

from ..context_processors import project_settings

class ProjectSettingsTestCase(TestCase):
    
    def setUp(self):
        setattr(settings, 'GA_TRACKING_CODE', 'TEST_CODE')
    
    def test_project_settings(self):
        result = project_settings(HttpRequest())
        self.assertEqual(len(result), 1)
        self.assertEqual(result['settings']['GA_TRACKING_CODE'], 'TEST_CODE')
