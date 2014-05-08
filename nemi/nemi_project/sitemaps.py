
from django.contrib.sitemaps import Sitemap;

from common.models import Method, SourceCitationRef

class MethodSitemap(Sitemap):

    changefreq = 'monthly'

    def items(self):
        return Method.objects.all().exclude(method_subcategory_id__in=[16, 17])

    def location(self, obj):
        return '/methods/method_summary/' + str(obj.method_id) + '/'

    def lastmod(self, obj):
        return obj.last_update_date


class ProtocolSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return SourceCitationRef.protocol_objects.all()

    def location(self, obj):
        return '/protocols/protocol_sumary/' + str(obj.source_citation_id) + '/'

    def lastmod(self, obj):
        return obj.update_date


class StatisticalMethodSitemap(Sitemap):

    changefreq = 'monthly'

    def items(self):
        return Method.objects.all().filter(method_subcategory_id__in=[16, 17])

    def location(self, obj):
        return '/methods/sams_method_summary/' + str(obj.method_id) + '/'

    def lastmod(self, obj):
        return obj.last_update_date

class StaticSitemap(Sitemap):

    def items(self):
        return ['/methods/browse_methods/', '/home/', '/glossary/', '/protocols/browse/']

    def location(self, item):
        return item

