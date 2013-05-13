
import datetime;

from django.test import TestCase

from ..models import NewsItem
from ..views import RecentNewsMixin

class RecentNewsMixinTestCase(TestCase):
    
    def setUp(self):
        self.mixin = RecentNewsMixin()
    
    def test_no_items(self):
        self.assertQuerysetEqual(self.mixin.get_context_data()['news_items'], []);
        
    def test_all_items_latest(self):
        today = datetime.date.today()
        
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n2.created = today - datetime.timedelta(days=50)
        n2.save()
        n3.created = today - datetime.timedelta(days=365*2)
        n3.save()
        
        self.assertQuerysetEqual(self.mixin.get_context_data()['news_items'], [repr(n1), repr(n2), repr(n3)] )

    def test_some_items_in_latest(self):
        today = datetime.date.today()
        
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n2.created = today - datetime.timedelta(days=50)
        n2.save()
        n3.created = today - datetime.timedelta(days=365*2 + 1)
        n3.save()
        
        self.assertQuerysetEqual(self.mixin.get_context_data()['news_items'], [repr(n1), repr(n2)])
        
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
        
        self.assertQuerysetEqual(self.mixin.get_context_data()['news_items'], [])
        
    def test_return_latest_ten(self):
        n1 = NewsItem.objects.create(headline='Headline 1')
        n2 = NewsItem.objects.create(headline='Headline 2')
        n3 = NewsItem.objects.create(headline='Headline 3')
        n4 = NewsItem.objects.create(headline='Headline 3')
        n5 = NewsItem.objects.create(headline='Headline 4')
        n6 = NewsItem.objects.create(headline='Headline 5')
        n7 = NewsItem.objects.create(headline='Headline 6')
        n8 = NewsItem.objects.create(headline='Headline 7')
        n9 = NewsItem.objects.create(headline='Headline 8')
        n10 = NewsItem.objects.create(headline='Headline 9')
        n11 = NewsItem.objects.create(headline='Headline 10')
        n12 = NewsItem.objects.create(headline='Headline 11')
        
        today = datetime.date.today()
        
        n1.created = today - datetime.timedelta(days=30)
        n1.save()
        n2.created = today - datetime.timedelta(days=29)
        n2.save()
        n3.created = today - datetime.timedelta(days=25)
        n3.save()
        n4.created = today - datetime.timedelta(days=20)
        n4.save()
        n5.created = today - datetime.timedelta(days=15)
        n5.save()
        n6.created = today - datetime.timedelta(days=10)
        n6.save()
        n7.created = today - datetime.timedelta(days=5)
        n7.save()
        n8.created = today - datetime.timedelta(days=4)
        n8.save()
        n9.created = today - datetime.timedelta(days=3)
        n9.save()
        n10.created = today - datetime.timedelta(days=2)
        n10.save()
        n11.created = today - datetime.timedelta(days=1)
        n11.save()
        
        self.assertQuerysetEqual(self.mixin.get_context_data()['news_items'],
                                 [repr(n12),
                                  repr(n11),
                                  repr(n10),
                                  repr(n9),
                                  repr(n8),
                                  repr(n7),
                                  repr(n6),
                                  repr(n5),
                                  repr(n4),
                                  repr(n3),
                                  ]
                                 )