'''
Created on Jul 25, 2012

@author: mbucknel
'''
from django.db.models import Model, CharField

class TestModel(Model):
    name = CharField(max_length=20, blank=False)
    
    def __unicode__(self):
        return self.name    
        