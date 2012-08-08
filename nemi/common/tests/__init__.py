
from django.utils import unittest

import test_forms
import test_models
import test_templatetags
import test_utils

def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_utils)
    suite2 = unittest.TestLoader().loadTestsFromModule(test_templatetags)
    suite3 = unittest.TestLoader().loadTestsFromModule(test_forms)
    suite4 = unittest.TestLoader().loadTestsFromModule(test_models)
    
    alltests = unittest.TestSuite([suite1, suite2, suite3, suite4])
    
    return alltests

def load_tests(loader, tests, pattern):
    return suite