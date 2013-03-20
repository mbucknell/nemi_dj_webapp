from django.utils import unittest

import test_context_processors

def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_context_processors)
    
    alltests = unittest.TestSuite([suite1])
    
    return alltests

def load_tests(loader, tests, pattern):
    return suite()