
from django.utils import unittest

import test_utils
import test_templatetags

def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_utils)
    suite2 = unittest.TestLoader().loadTestsFromModule(test_templatetags)
    
    alltests = unittest.TestSuite([suite1, suite2])
    
    return alltests

def load_tests(loader, tests, pattern):
    return suite