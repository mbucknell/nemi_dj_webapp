from datetime import datetime

from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from nemi_project.admin import method_admin

from . import models


class ReferenceTableAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    fieldsets = (
        (None, {
            'fields': (
                ('data_entry_name', 'data_entry_date'),
                ('update_name', 'update_date'),
            ),
        }),
    )
    readonly_fields = (
        'data_entry_name', 'data_entry_date', 'update_name', 'update_date'
    )

    def is_method_admin(self, request, *args, **kwargs):
        if not hasattr(self, '_admin'):
            self._is_admin = request.user.groups.filter(
                name='method_admin').exists()
        return self._is_admin

    def audit_instance(self, username, obj):
        obj.update_name = username
        obj.update_date = datetime.now()
        if not obj.pk:
            obj.data_entry_name = username
            obj.data_entry_date = obj.update_date

    def save_model(self, request, obj, form, change):
        self.audit_instance(request.user.username, obj)
        return super(ReferenceTableAdmin, self).save_model(request, obj, form, change)

    has_module_permission = is_method_admin
    has_add_permission = is_method_admin
    has_change_permission = is_method_admin
    has_delete_permission = is_method_admin


class AccuracyUnitsDomAdmin(ReferenceTableAdmin):
    class Meta:
        model = models.AccuracyUnitsDom

    list_display = (
        'accuracy_units', 'accuracy_units_description'
    ) + ReferenceTableAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': (
                'accuracy_units',
                'accuracy_units_description',
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets


class AnalyteCodeRelAdmin(admin.TabularInline):
    model = models.AnalyteCodeRel
    extra = 0
    fields = ('analyte_name', 'preferred') + ReferenceTableAdmin.readonly_fields
    readonly_fields = ReferenceTableAdmin.readonly_fields

    def save_model(self, request, obj, form, change):
        self.audit_instance(request, obj, change)
        return super(AnalyteCodeRelAdmin, self).save_model(request, obj, form, change)


class AnalyteRefAdmin(ReferenceTableAdmin):
    class Meta:
        model = models.AnalyteRef

    inlines = (AnalyteCodeRelAdmin,)
    list_display = ('analyte_code', 'analyte_type', 'analyte_cbr')
    fieldsets = (
        (None, {
            'fields': (
                'analyte_code', 'analyte_type', 'analyte_cbr', 'usgs_pcode',
                'analyte_code_cbr',
                # These two are in the database but not in the APEX UI:
                #'cbr_analyte_category', 'cbr_analyte_intro'
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets

    def save_model(self, request, obj, form, change):
        self.audit_instance(request.user.username, obj)
        return super(AnalyteRefAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in formset.deleted_objects:
            instance.delete()
        for instance in instances:
            self.audit_instance(request.user.username, instance)
            instance.save()
        formset.save_m2m()


class DlRefAdmin(ReferenceTableAdmin):
    class Meta:
        model = models.DlRef

    list_display = (
        'dl_type_id', 'dl_type', 'dl_type_description'
    ) + ReferenceTableAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': (
                'dl_type', 'dl_type_description'
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets
    ordering = ('dl_type_id',)


class DlUnitsDomAdmin(ReferenceTableAdmin):
    class Meta:
        model = models.DlUnitsDom

    list_display = (
        'dl_units', 'dl_units_description') + ReferenceTableAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': (
                'dl_units', 'dl_units_description'
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ReferenceTableAdmin.readonly_fields
        # If we're editing, don't allow changing the primary key
        if obj:
            readonly_fields += ('dl_units',)
        return readonly_fields


class InstrumentationRefAdmin(ReferenceTableAdmin):
    list_display = (
        'instrumentation', 'instrumentation_description'
    ) + ReferenceTableAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': (
                'instrumentation', 'instrumentation_description'
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets


class MethodSourceRefForm(forms.ModelForm):
    class Meta:
        model = models.MethodSourceRef
        fields = '__all__'
        widgets = {
            'method_source_contact': TinyMCE(attrs={'cols': 100, 'rows': 50})
        }


class MethodSourceRefAdmin(ReferenceTableAdmin):
    form = MethodSourceRefForm
    list_display = (
        'method_source', 'method_source_url', 'method_source_name',
        'method_source_contact', 'method_source_email'
    ) + ReferenceTableAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': (
                'method_source', 'method_source_url', 'method_source_name',
                'method_source_contact', 'method_source_email'
            ),
        }),
    ) + ReferenceTableAdmin.fieldsets


method_admin.register(models.AccuracyUnitsDom, AccuracyUnitsDomAdmin)
method_admin.register(models.AnalyteRef, AnalyteRefAdmin)
method_admin.register(models.DlRef, DlRefAdmin)
method_admin.register(models.DlUnitsDom, DlUnitsDomAdmin)
method_admin.register(models.InstrumentationRef, InstrumentationRefAdmin)
method_admin.register(models.MethodSourceRef, MethodSourceRefAdmin)
