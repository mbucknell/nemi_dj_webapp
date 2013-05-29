
from django.contrib.sitemaps import Sitemap;
from django.core.urlresolvers import reverse

from common.models import Method

class MethodSitemap(Sitemap):
    
    changefreq = 'monthly'
    
    def items(self):
        return Method.objects.all().exclude(method_subcategory_id__in=[16, 17])
    
    def location(self, obj):
        return reverse('methods-method_summary', args=[obj.method_id])
    
    def lastmod(self, obj):
        return obj.last_update_date
    
class StatisticalMethodSitemap(Sitemap):
    
    changefreq = 'monthly'
    
    def items(self):
        return Method.objects.all().filter(method_subcategory_id__in=[16,17])
    
    def location(self, obj):
        return reverse('methods-sam_method_summary', args=[obj.method_id])
    
    def lastmod(self, obj):
        return obj.last_update_date

class StaticSitemap(Sitemap):
    
    def items(self):
        return ['methods-browse', 'home']
    
    def location(self, item):
        return reverse(item)