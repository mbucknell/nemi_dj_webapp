'''
Created on Mar 13, 2012

@author: mbucknel
'''

from django.utils import unittest

from methods.views import _clean_name, _clean_keyword

class CleanNameTestCase(unittest.TestCase):

    def test_clean_name(self):
        name = 'a256&B*-_Z'
        self.assertEqual(name, _clean_name(name))
        
        name = 'a<sub>3</sub>43ABc'
        self.assertEqual('a343ABc', _clean_name(name))
        
        name = 'a(3)43ABC'
        self.assertEqual('a343ABC', _clean_name(name))
        
        name = 'a#343ABC'
        self.assertEqual('a343ABC', _clean_name(name))
        
        name = 'a 343ABC'
        self.assertEqual('a_343ABC', _clean_name(name))
        
        name = 'a3,4,3ABC'
        self.assertEqual('a3_4_3ABC', _clean_name(name))
        
        name = 'a3/43/ABC'
        self.assertEqual('a3_43_ABC', _clean_name(name)) 
        
        name = 'a3/43.ABC'
        self.assertEqual('a3_43_ABC', _clean_name(name))
        
        name = 'a3<sub>4</sub>3 ABC'
        self.assertEqual('a343_ABC', _clean_name(name))
           

class CleanKeywordTestCase(unittest.TestCase):
    
    def test_with_no_special_characters(self):
        keyword='nitrate'
        self.assertEqual(_clean_keyword(keyword), '{nitrate}')
        
    def test_with_one_dash(self):
        keyword = 'ni-trate'
        self.assertEqual(_clean_keyword(keyword), '{ni-trate}')
        
    def test_with_one_comma(self):
        keyword = 'ni,trate'
        self.assertEqual(_clean_keyword(keyword), '{ni,trate}')
        
    def test_with_quote(self):
        keyword = "ni'trate"
        self.assertEqual(_clean_keyword(keyword), "{ni''trate}")
        
    def test_with_two_quotes(self):
        keyword = "ni'trate'chloride"
        self.assertEqual(_clean_keyword(keyword), "{ni''trate''chloride}")
        
    def test_with_double_quotes(self):
        keyword = 'ni"trate'
        self.assertEqual(_clean_keyword(keyword), '{ni""trate}')
        
    def test_with_two_double_quotes(self):
        keyword = 'ni"trate"chloride'
        self.assertEqual(_clean_keyword(keyword), '{ni""trate""chloride}')
               
        
       
