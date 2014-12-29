from django.test import TestCase

from ..models import HelpContent
from ..templatetags.helpcontent import get_help_content

'''
class GetHelpContentTestCase(TestCase):
    
    def test_string_value(self):
        value = "Random string"
        name = "name_1"
        ghc = get_help_content(value, name)
        hc = HelpContent(field_name='name1', label='Name 1')
        self.assertEqual(ghc, hc)
        
    def test_dict_object_without_labels(self):
        class TestObj(object):
            field_name = '';
            
        m1 = TestObj()
        m1.field_name = 'name_1'
        m2 = TestObj()
        m2.field_name='name_2'
        
        self.assertEqual(get_help_content({'name_1': m1, 'name_2': m2}, 'name_1'), HelpContent(field_name='name_1', label='Name 1'))

    def test_dict_object_without_field_names(self):
        class TestObj(object):
            label = '';
        m1 = TestObj()
        m1.label = 'Django Name 1'
        m2 = TestObj()
        m2.label = 'Django Name 2'
        
        self.assertEqual(get_help_content({'name_1': m1, 'name_2': m2}, 'name_1'), HelpContent(field_name='name_1', label='Name 1'))

    def test_with_help_content_model(self):
        m1 = HelpContent(field_name='name_1', label='Django Name 1', description="Description 1")
        m2 = HelpContent(field_name='name_2', label='Django Name 2', description="Description 2")
        
        self.assertEqual(get_help_content({'name_1': m1, 'name_2': m2}, 'name_1'), m1)
        
    def test_with_help_content_model_missing_name(self):
        m1 = HelpContent.objects.create(field_name='name_1', label='Django Name 1')
        m2 = HelpContent.objects.create(field_name='name_2', label='Django Name 2')
        
        self.assertEqual(get_help_content({'name_1': m1, 'name_2': m2}, 'this_name'), 
                         HelpContent(field_name='name1', label='This Name'))  
                         '''