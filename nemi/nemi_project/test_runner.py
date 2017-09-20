'''
Created on Mar 14, 2012

@author: mbucknel
'''
from collections import defaultdict

from django.apps import apps
from django.test.runner import DiscoverRunner


def field_count(model_class):
    return len([
        f
        for f in model_class._meta.get_fields()
        if f.concrete and (
            not f.is_relation
            or f.one_to_one
            or (f.many_to_one and f.related_model)
        )
    ])


# I got this snippet from http://www.caktusgroup.com/blog/2010/09/24/simplifying-the-testing-of-unmanaged-database-models-in-django/
class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """
    def setup_test_environment(self, *args, **kwargs):
        # To handle the case where we have more than one unmanaged model per
        # table, treat the model with more fields as the "managed" version.

        models_by_table = defaultdict(list)
        for model in apps.get_models(include_auto_created=True):
            lst = models_by_table.setdefault(model._meta.db_table, [])
            lst.append(model)

        self.unmanaged_models = [
            max(models, key=field_count)
            for _, models in models_by_table.items()
        ]

        for m in self.unmanaged_models:
            m._meta.managed = True

        super(ManagedModelTestRunner, self).setup_test_environment(*args,
                                                                   **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).teardown_test_environment(*args,
                                                                      **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
