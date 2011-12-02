''' Module includes all urls confs for the nemi project '''

from django.conf.urls.defaults import patterns, include, url

import search.urls

urlpatterns = patterns('',
    url(r'^search/', include(search.urls)),
)
