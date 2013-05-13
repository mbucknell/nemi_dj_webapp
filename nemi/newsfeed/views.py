
import datetime

from django.views.generic.base import ContextMixin

from .models import NewsItem

class RecentNewsMixin(ContextMixin):
    '''
    Extends ContentMixin to add the last 10 news items within the last two years to the context in the news_items key.
    '''
    def get_context_data(self, **kwargs):
        context = super(RecentNewsMixin, self).get_context_data(**kwargs)
        
        today = datetime.date.today()
        start = today - datetime.timedelta(days=365 * 2)
        
        context['news_items'] = NewsItem.objects.filter(created__range=(start, today))[:10]
        
        return context;
            