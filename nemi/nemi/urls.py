''' Module includes all urls confs for the nemi project '''


from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import search.urls

urlpatterns = patterns('',
    url(r'^search/', include(search.urls)),
)

urlpatterns += staticfiles_urlpatterns()
