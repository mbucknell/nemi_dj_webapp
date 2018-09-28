''' Module includes all urls confs for the nemi project '''

from django.conf.urls import include, url
from django.contrib import admin
import django.contrib.auth.views
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages.views import flatpage as flatpage_view
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

import domhelp
import methods.urls
import protocols.urls
import sams.urls

from .admin import method_admin
from . import sitemaps
from . import views


admin.autodiscover()

sitemaps = {
    'flatpages' : FlatPageSitemap,
    'staticpages' : sitemaps.StaticSitemap,
    'methods' : sitemaps.MethodSitemap,
    'protocols' : sitemaps.ProtocolSitemap,
    'statisticalmethods' : sitemaps.StatisticalMethodSitemap
}

urlpatterns = [
    url(r'^version/', views.version, {}, name='nemi_version'),
    url(r'^admin/', admin.site.urls),
    url(r'^method-submission/', method_admin.urls),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^ie8_error/$',
        TemplateView.as_view(template_name='ie8_error_page.html'),
        name='ie8_error_page'),

    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^accounts/login/$',
        django.contrib.auth.views.LoginView.as_view(),
        {},
        name='nemi_login'),
    url(r'^accounts/logout/$',
        django.contrib.auth.views.LogoutView.as_view(),
        {'redirect_field_name' : 'redirect_url'},
        name='nemi_logout'),
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
    url(r'^protocols/', include(protocols.urls)),

    url(r'^sams/', include(sams.urls)),
    # url(r'^memo/', include(memo.urls)),

    url(r'^home/',
        views.HomeView.as_view(),
        name='home'),
    url(r'^method_entry/',
        views.MethodEntryView.as_view(),
        name='method_entry'),
    url(r'^glossary/',
        domhelp.views.GlossaryView.as_view(),
        name='glossary'),
]

urlpatterns += methods.urls.api_urlpatterns

urlpatterns += [
    url(r'^about/$', flatpage_view, {'url' : '/about/'}, name='about'),
    url(r'^faqs/$', flatpage_view, {'url' : '/faqs/'}, name='faqs'),
    url(r'^submit_method/$', flatpage_view, {'url' : '/submit_method/'}, name='submit_method'),
    url(r'^terms_of_use/$', flatpage_view, {'url' : '/terms_of_use/'}, name='terms_of_use')
]
