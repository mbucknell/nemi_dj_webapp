'''
Created on Aug 1, 2012

@author: mbucknel
'''

from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

from common.models import MethodAbstract, StatisticalItemType, MethodTypeRef

class TestMethodGetInsertUser(TestCase):
    
    class DummyMethod(MethodAbstract):
        dummyField = models.IntegerField()
        
    def setUp(self):
        self.u1 = User.objects.create('user1', password='password1')
        self.u2 = User.objects.create('user2', password='password2')
        
        self.item_type = StatisticalItemType.objects.create(stat_item_index=1, item='Stat Item')
        self.method_type = MethodTypeRef.objects.create(method_type_id=1, method_type_desc='method_type_desc')
        
        self.m1 = self.DummyMethod.objects.create(source_method_identifier='id1',
                                                  method_official_name='name1',
                                                  brief_method_summary='summary1',
                                                  insert_person_name='user1',
                                                  method_type=self.method_type)
        self.m2 = self.DummyMethod.objects.create(source_method_identifier='id2',
                                                  method_official_name='name2',
                                                  brief_method_summary='summary2',
                                                  insert_person_name='user3',
                                                  method_type=self.method_type)
        
        def test_get_insert_user(self):
            self.assertEqual(self.m1.get_insert_user(), self.u1)
            self.assertEqual(self.m2.get_insert_user().username, 'Unknown')
        