''' Module includes all urls confs for the nemi project '''

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from django.views.generic import TemplateView

import domhelp
import methods.urls
import sams.urls
#import memo.urls

import sitemaps
import views

admin.autodiscover()

sitemaps = {
    'flatpages' : FlatPageSitemap,
    'staticpages' : sitemaps.StaticSitemap,
    'methods' : sitemaps.MethodSitemap,
    'statisticalmethods' : sitemaps.StatisticalMethodSitemap
    }

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', 
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^ie3_error/$', 
        TemplateView.as_view(template_name='ie8_error_page.html'),
        name='ie8_error_page'),
    
    url(r'^tinymce/', include('tinymce.urls')),
    
    url(r'^accounts/login/$', 
        'django.contrib.auth.views.login', 
        {}, 
        name='nemi_login'),
    url(r'^accounts/logout/$', 
        'django.contrib.auth.views.logout', 
        {'redirect_field_name' : 'redirect_url'}, 
        name="nemi_logout"),
    url(r'^accounts/password_change/$',
        views.PasswordChangeView.as_view(),
        name='nemi_change_password'),
    url(r'^accounts/create_account/$', 
        views.CreateUserView.as_view(), 
        name='nemi_create_account'),
    url(r'^accounts/create_account_success$', 
        TemplateView.as_view(template_name="registration/create_account_success.html"), 
        name="nemi_create_account_success"),
                       
    url(r'^methods/', include(methods.urls)),
    url(r'^sams/', include(sams.urls)),
#	url(r'^memo/', include(memo.urls)),

    url(r'^home/', 
        views.HomeView.as_view(),
        name='home'),
    url(r'^method_entry/',
        views.MethodEntryView.as_view(),
        name='method_entry'),
    url(r'^glossary/',
        domhelp.views.GlossaryView.as_view(),
        name='glossary'),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url' : '/about/'}, name='about'),
    url(r'^faqs/$', 'flatpage', {'url' : '/faqs/'}, name='faqs'),
    url(r'^submit_method/$', 'flatpage', {'url' : '/submit_method/'}, name='submit_method'),
    url(r'^terms_of_use/$', 'flatpage', {'url' : '/terms_of_use/'}, name='terms_of_use'));
