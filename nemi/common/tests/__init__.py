import unittest

from . import test_models
from . import test_templatetags
from . import test_utils
from . import test_views
from . import test_context_processors
from . import test_method_admin
from . import test_fields


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(test_utils),
        unittest.TestLoader().loadTestsFromModule(test_templatetags),
        unittest.TestLoader().loadTestsFromModule(test_models),
        unittest.TestLoader().loadTestsFromModule(test_views),
        unittest.TestLoader().loadTestsFromModule(test_context_processors),
        unittest.TestLoader().loadTestsFromModule(test_method_admin),
        unittest.TestLoader().loadTestsFromModule(test_fields),
    ])


def load_tests(loader, tests, pattern):
    return suite()
