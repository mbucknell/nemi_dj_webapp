
from django.test import TestCase

from ..models import HelpContent
from ..views import FieldHelpMixin

class FieldHelpMixinTestCase(TestCase):
    
    def setUp(self):
        self.h1 = HelpContent.objects.create(field_name='name_1', label='Django Name 1')
        self.h2 = HelpContent.objects.create(field_name='name_2', label='Django Name 2')
        self.h3 = HelpContent.objects.create(field_name='name_3', label='Django Name 3')
        
    def test_get_all(self):
        test_mixin = FieldHelpMixin()
        self.assertEqual(test_mixin.get_context_data()['field_help'], {self.h1.field_name: self.h1, self.h2.field_name: self.h2, self.h3.field_name: self.h3})
        
    def test_get_some(self):
        class TestFieldHelpMixin(FieldHelpMixin):
            field_names = ['name_1', 'name_3']
            
        test_mixin = TestFieldHelpMixin()
        
        self.assertEqual(test_mixin.get_context_data()['field_help'], {self.h1.field_name: self.h1, self.h3.field_name: self.h3})
