from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ..models import HelpContent

class FieldNameValidatorTestCase(SimpleTestCase):
    
    def test_valid_field_name(self):
        c1 = HelpContent.objects.create(field_name='my1_name', label='My Name')

        self.assertIsNone(c1.full_clean())
        
    def test_leading_underscore_field_name(self):
        c1 = HelpContent.objects.create(field_name='_my1_name', label='My Name')
        with self.assertRaises(ValidationError):
            c1.full_clean()
        
    def test_trailing_underscore_field_name(self):
        c1 = HelpContent.objects.create(field_name='my1_name_', label='My Name')
        with self.assertRaises(ValidationError):
            c1.full_clean()
        
    def test_non_alphanumeric_characters_field_name(self):
        c1 = HelpContent.objects.create(field_name='my%_name', label='My Name')
        with self.assertRaises(ValidationError):
            c1.full_clean()
