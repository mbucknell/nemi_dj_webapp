'''
Created on Mar 13, 2012

@author: mbucknel
'''

from django.utils import unittest

from methods.views import _clean_name

class TestCleanName(unittest.TestCase):

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
           

