
from django.utils import unittest

import test_templatetags
import test_utils


def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_templatetags)
    suite2 = unittest.TestLoader().loadTestsFromModule(test_utils)
    
    alltests = unittest.TestSuite([suite1, suite2])
    
    return alltests
    
def load_tests(loader, tests, pattern):
    return suite()