
from django.http import HttpRequest
from django.test import TestCase

from ..models import NewsItem
from ..context_processors import latest_news_items

import datetime


class LatestNewsItemsTestCase(TestCase):
    
    def test_no_items(self):
        self.assertQuerysetEqual(latest_news_items(HttpRequest())['news_items'], [])
       
    def test_all_items_latest(self):
        today = datetime.date.today()
        
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n2.created = today - datetime.timedelta(days=50)
        n2.save()
        n3.created = today - datetime.timedelta(days=365*2)
        n3.save()
        
        self.assertQuerysetEqual(latest_news_items(HttpRequest())['news_items'], [repr(n1), repr(n2), repr(n3)] )
        
    def test_some_items_in_latest(self):
        today = datetime.date.today()
        
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n2.created = today - datetime.timedelta(days=50)
        n2.save()
        n3.created = today - datetime.timedelta(days=365*2 + 1)
        n3.save()
        
        self.assertQuerysetEqual(latest_news_items(HttpRequest())['news_items'], [repr(n1), repr(n2)])
        
    def test_all_items_not_in_latest(self):
        today = datetime.date.today()
        
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n1.created = today - datetime.timedelta(days=365*2 + 1)
        n1.save()
        n2.created = today - datetime.timedelta(days=365*3)
        n2.save()
        n3.created = today - datetime.timedelta(days=365*4)
        n3.save()
        
        self.assertQuerysetEqual(latest_news_items(HttpRequest())['news_items'], [])
        
        
        
        
        
        