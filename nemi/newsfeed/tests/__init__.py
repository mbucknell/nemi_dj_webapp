import unittest

from . import test_context_processors
from . import test_views


def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_context_processors)
    suite2 = unittest.TestLoader().loadTestsFromModule(test_views)

    alltests = unittest.TestSuite([suite1, suite2])

    return alltests

def load_tests(loader, tests, pattern):
    return suite()
