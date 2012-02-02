''' Module includes all urls confs for the nemi project '''

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

import search.urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^search/', include(search.urls)),
)
