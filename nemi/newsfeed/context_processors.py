from .models import NewsItem

import datetime

def latest_news_items(request):
    context = {}
    
    today = datetime.date.today()
    start = today - datetime.timedelta(days=365 * 2)
    
    context['news_items'] = NewsItem.objects.filter(created__range=(start, today))[:10]
    
    return context
                                                    
    
