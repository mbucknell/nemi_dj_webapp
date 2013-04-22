
from django.forms import CharField, IntegerField
from django.utils import unittest

from ..forms import BaseDefinitionsForm
from ..models import HelpContent

class BaseDefinitionsFormTestCase(unittest.TestCase):
    
    def setUp(self):
        self.d1 = HelpContent.objects.create(field_name='one', label='One label', tooltip='One tooltip', description='One field help text')
        self.d2 = HelpContent.objects.create(field_name='two', label='Two label', tooltip='', description='Two field help text')
        self.d3 = HelpContent.objects.create(field_name='three', label='', tooltip='Three tooltip', description='')

    def test_form_properties(self):

        class TestForm(BaseDefinitionsForm):
            one = CharField(max_length=10)
            two = CharField(max_length=10, label='Redefined two label', help_text='Redefined two help text')
            three = IntegerField(label='Redefined three label', help_text='Redefined three help text')
            four = IntegerField(label='Four label', help_text='Four help text')
            
        form = TestForm()
        
        #Tests that properties from WebFormDefinition are used for field one
        self.assertEqual(form.fields['one'].label, self.d1.label)
        self.assertEqual(form.fields['one'].tooltip, self.d1.tooltip)
        self.assertEqual(form.fields['one'].help_text, self.d1.description)

        # Tests that WebFormDefinitions if present override setting in form field definition and that missing properties are not found.
        self.assertEqual(form.fields['two'].label, self.d2.label)
        with self.assertRaises(AttributeError):
            t = form.fields['two'].tooltip
        self.assertEqual(form.fields['two'].help_text, self.d2.description)
        
        #Tests that form definitions are used if attributes field values are null in WebFormDefinitions
        self.assertEqual(form.fields['three'].label, 'Redefined three label')
        self.assertEqual(form.fields['three'].tooltip, self.d3.tooltip)
        self.assertEqual(form.fields['three'].help_text, 'Redefined three help text')
        
        # Tests missing WebFormDefinitions object for a field
        self.assertEqual(form.fields['four'].label, 'Four label')
        with self.assertRaises(AttributeError):
            t = form.fields['four'].tooltip
        self.assertEqual(form.fields['four'].help_text, 'Four help text')
        
        
       
        