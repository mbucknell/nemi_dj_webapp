from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.forms import ModelForm
from tinymce.widgets import TinyMCE


class FlatPageForm(ModelForm):
    class Meta:
        model = FlatPage
        fields = '__all__'
        widgets = {'content': TinyMCE(attrs={'cols': 100, 'rows': 50})}


class FlatPageAdmin(admin.ModelAdmin):
    form = FlatPageForm


class MethodAdminSite(admin.AdminSite):
    site_header = 'NEMI Method Manager'
    site_title = 'NEMI Method Manager'
    index_title = 'Method submission'

    def __init__(self, *args, **kwargs):
        super(MethodAdminSite, self).__init__(*args, **kwargs)
        self.name = 'method_admin'

    def has_permission(self, request):
        """
        All active users have method submission permission.
        """
        return request.user.is_active


method_admin = MethodAdminSite(name='method_submission')

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
