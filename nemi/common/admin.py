from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.forms import ModelForm
from tinymce.widgets import TinyMCE

from . import models


class FlatPageForm(ModelForm):

    class Meta:
        model = FlatPage
        fields = '__all__'
        widgets = {'content': TinyMCE(attrs={'cols': 100, 'rows': 50})}


class FlatPageAdmin(admin.ModelAdmin):

    form = FlatPageForm


class MethodAdmin(admin.ModelAdmin):
    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date'
    )
    class Meta:
        model = models.Method
        fields = '__all__'


class MethodOnlineAdmin(admin.ModelAdmin):
    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date'
    )
    class Meta:
        model = models.MethodOnline
        fields = '__all__'


class MethodStgAdmin(admin.ModelAdmin):
    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date'
    )
    class Meta:
        model = models.MethodStg
        fields = '__all__'


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(models.Method, MethodAdmin)
admin.site.register(models.MethodOnline, MethodOnlineAdmin)
admin.site.register(models.MethodStg, MethodStgAdmin)
