
from django.contrib.sitemaps import Sitemap;
from django.core.urlresolvers import reverse

from common.models import Method

class MethodSitemap(Sitemap):
    
    changefreq = 'monthly'
    
    def items(self):
        return Method.objects.all().exclude(method_subcategory_id__in=[16, 17])
    
    def location(self, obj):
        return '/methods/method_summary/' + str(obj.method_id) +'/'
    
    def lastmod(self, obj):
        return obj.last_update_date
    
class StatisticalMethodSitemap(Sitemap):
    
    changefreq = 'monthly'
    
    def items(self):
        return Method.objects.all().filter(method_subcategory_id__in=[16,17])
    
    def location(self, obj):
        return '/methods/method-sam_method_summary/' + str(obj.method_id) + '/'
    
    def lastmod(self, obj):
        return obj.last_update_date

class StaticSitemap(Sitemap):
    
    def items(self):
        return ['/methods/browse_methods/', '/home/', '/glossary/']
    
    def location(self, item):
        return item
    
