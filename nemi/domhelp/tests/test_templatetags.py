
from django.test import TestCase

from nemi_project.test_settings_mgr import TestSettingsManager

from models import TestModel
from ..models import HelpContent
from ..templatetags.helpcontent import get_help_content


class GetHelpContentTestCase(TestCase):
    
    def __init__(self, *args, **kwargs):
        super(GetHelpContentTestCase, self).__init__(*args, **kwargs)
        self.settings_manager = TestSettingsManager()
        
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS = ('domhelp', 'domhelp.tests'))
    
    def test_string_value(self):
        value = "Random string"
        name = "name_1"
        self.assertIsNone(get_help_content(value, name))
        
    def test_model_without_field_name(self):
        m1 = TestModel.objects.create(name='name_1')
        m2 = TestModel.objects.create(name='name_2')
        
        self.assertIsNone(get_help_content(TestModel.objects.all(), 'name_1'))

    def test_with_help_content_model(self):
        m1 = HelpContent.objects.create(field_name='name_1', label='Django Name 1')
        m2 = HelpContent.objects.create(field_name='name_2', label='Django Name 2')
        
        self.assertEqual(get_help_content(HelpContent.objects.all(), 'name_1'), m1)
        
    def test_with_help_content_model_missing_name(self):
        m1 = HelpContent.objects.create(field_name='name_1', label='Django Name 1')
        m2 = HelpContent.objects.create(field_name='name_2', label='Django Name 2')
        
        self.assertEqual(get_help_content(HelpContent.objects.all(), 'this_name'), 
                         HelpContent(field_name='name1', label='This Name'))  