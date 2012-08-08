'''
Created on Mar 14, 2012

@author: mbucknel
'''
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.forms import Form, CharField
from django.utils import unittest

from common.templatetags.data_format import decimal_format, clickable_links
from common.templatetags.form_field_attr import tooltip
from common.templatetags.user_auth import in_group

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
        
class ClickableLinksTestCase(unittest.TestCase):
    def test_no_link(self):
        #Test with data that does not represent a link
        self.assertEqual(clickable_links('Hello'), 'Hello')
        
    def test_one_link(self):
        #Test with data with a single link
        link1 = 'http://www.usgs.gov'
        self.assertEqual(clickable_links(link1), 
                         '<a href="' + link1 + '">' + link1 + '</a>')
    
    def test_two_links(self):
        # Test with two links with various variation of the <br> tag as separators.
        link1 = 'http://www.usgs.gov'
        link2 = 'http://ww.epa.gov'
        result = '<a href="' + link1 + '">' + link1 + '</a>' + '<br />' + '<a href="' + link2 + '">' + link2 + '</a>'
        
        self.assertEqual(clickable_links(link1 + '<br>' + link2), result)
        self.assertEqual(clickable_links(link1 + '<br/>' + link2), result)
        self.assertEqual(clickable_links(link1 + '<br />' + link2), result)
    
    def test_two_links_bad_break_tag(self):
        # Test with two links but with a malformed break tag
        link1 = 'http://www.usgs.gov'
        link2 = 'http://www.epa.gov'
        result = '<a href="' + link1 + '">' + link1 + '</a>' + '<br />' + '<a href="' + link2 + '">' + link2 + '</a>'
        
        self.assertNotEqual(clickable_links(link1 + 'br>' + link2), result)
        self.assertNotEqual(clickable_links(link1 + '<br' + link2), result)
       
class TooltipTestCase(unittest.TestCase):
    
    def test_with_no_attributes(self):
        data = {'result1' : 1, 'result2' : 2}
        self.assertEqual(tooltip(data), settings.TEMPLATE_STRING_IF_INVALID)  
        
    def test_with_attribute(self):

        class MyForm(Form):
            my_field = CharField(max_length=1)
            
            def __init__(self, *args, **kwargs):
                super(MyForm, self).__init__(*args, **kwargs)
                self.fields['my_field'].tooltip = 'Tooltip'
            
        class MyBoundObject(object):
            form =  MyForm({'my_field' : 'A'}) 
            name = 'my_field'          

        test_object = MyBoundObject()
        self.assertEqual(tooltip(test_object), 'Tooltip')
        
class InGroupTestCase(unittest.TestCase):
    
    def setUp(self):
        self.g1 = Group.objects.create(name='group1')
        self.g2 = Group.objects.create(name='group2')
        self.g3 = Group.objects.create(name='group3')
        
    def test_in_group(self):
        self.assertFalse(in_group(None, self.g1.name)) 
        
        user = 'Some string'
        self.assertFalse(in_group(user, self.g1.name))       
        
        self.u1 = User.objects.create_user('user1')
        
        self.assertFalse(in_group(self.u1, self.g1.name))
        self.assertFalse(in_group(self.u1, '%s, %s, %s' % (self.g1.name, self.g2.name, self.g3.name)))
        
        self.u1.groups.add(self.g1)
        self.assertTrue(in_group(self.u1, self.g1.name))
        self.assertFalse(in_group(self.u1, self.g2.name))
        self.assertTrue(in_group(self.u1, '%s, %s' % (self.g1.name, self.g3.name)))
        self.assertFalse(in_group(self.u1, '%s, %s' % (self.g2.name, self.g3.name)))
        
        self.u1.groups.add(self.g2)
        self.assertTrue(in_group(self.u1, self.g1.name))
        self.assertTrue(in_group(self.u1, self.g2.name))
        self.assertTrue(in_group(self.u1, '%s, %s' % (self.g1.name, self.g3.name)))
        self.assertTrue(in_group(self.u1, '%s, %s' % (self.g2.name, self.g3.name)))
        self.assertFalse(in_group(self.u1, self.g3.name))
        
        