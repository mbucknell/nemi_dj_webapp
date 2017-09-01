'''
Created on Jul 25, 2012

@author: mbucknel
'''
from django.db.models import Model, CharField


class TestModel(Model):
    ''' Extends the base model to create a model used for running tests'''

    name = CharField(max_length=20, blank=False)

    def __str__(self):
        return self.name
