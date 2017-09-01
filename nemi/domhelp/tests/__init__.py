import unittest

from . import test_forms
from . import test_models
from . import test_templatetags
from . import test_views


def suite():
    suite1 = unittest.TestLoader().loadTestsFromModule(test_templatetags)
    suite2 = unittest.TestLoader().loadTestsFromModule(test_views)
    suite3 = unittest.TestLoader().loadTestsFromModule(test_models)
    suite4 = unittest.TestLoader().loadTestsFromModule(test_forms)

    alltests = unittest.TestSuite([suite1, suite2, suite3, suite4])

    return alltests


def load_tests(loader, tests, pattern):
    return suite()
