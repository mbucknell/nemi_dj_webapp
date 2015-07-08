import unittest

import test_views


def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_views)
    
    alltests = unittest.TestSuite([suite1])
    
    return alltests
    
def load_tests(loader, tests, pattern):
    return suite()