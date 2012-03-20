'''
Created on Mar 14, 2012

@author: mbucknel
'''
from django.conf import settings
from django.forms import Form, CharField
from django.utils import unittest
from nemi.search.templatetags.data_format import decimal_format, obey_linefeeds
from nemi.search.templatetags.form_field_attr import verbose_help


class DecimalFormatTestCase(unittest.TestCase):

    def test_string(self):
        # Test with a string, should return back the string
        self.assertEqual(decimal_format('data string'), 'data string');
        
    def test_integer(self):
        #Test with an integer number
        self.assertEqual(decimal_format(14), 14)
        
    def test_decimal_no_fraction(self):
        #Test with decimal number with no fraction part
        self.assertEqual(decimal_format(14.0000), 14)

    def test_decimal_with_fraction(self):
        #Test with a decimal number with a fraction part
        self.assertEqual(decimal_format(14.56000), 14.56)
        
    def test_decimal_with_no_integer_part(self):
        #Test with a decimal number with no integer part
        self.assertEqual(decimal_format(.567), 0.567)
        
class ObeyLineFeedsTestCase(unittest.TestCase):
    
    def test_with_no_lfs(self):
        self.assertEqual(obey_linefeeds('Test data with no lfs'), 'Test data with no lfs')

    def test_with_lfs(self):
        self.assertEqual(obey_linefeeds('Test data line 1\nTest data line 2'), 'Test data line 1<br />Test data line 2')
        self.assertEqual(obey_linefeeds('Line 1\nLine 2\nLine 3'), 'Line 1<br />Line 2<br />Line 3')
        
class VerboseHelpTestCase(unittest.TestCase):
    
    def test_with_no_attributes(self):
        data = {'result1' : 1, 'result2' : 2}
        self.assertEqual(verbose_help(data), settings.TEMPLATE_STRING_IF_INVALID)  
        
    def test_with_attribute(self):

        class MyForm(Form):
            my_field = CharField(max_length=1)
            
            def __init__(self, *args, **kwargs):
                super(MyForm, self).__init__(*args, **kwargs)
                self.fields['my_field'].verbose_help = 'Verbose help'
            
        class MyBoundObject(object):
            form =  MyForm({'my_field' : 'A'}) 
            name = 'my_field'          

        test_object = MyBoundObject()
        self.assertEqual(verbose_help(test_object), 'Verbose help')   