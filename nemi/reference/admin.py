from datetime import datetime

from django.contrib import admin

from nemi_project.admin import method_admin

from . import models


class UserTimestampMixin:
    fields = (
        'data_entry_name', 'data_entry_date', 'update_name', 'update_date'
    )
    readonly_fields = (
        'data_entry_name', 'data_entry_date', 'update_name', 'update_date'
    )

    def save_model(self, request, obj, form, change):
        self.audit_instance(request.user.username, obj)
        return super(UserTimestampMixin, self).save_model(request, obj, form, change)


class ReferenceTableAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

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

    has_module_permission = is_method_admin
    has_add_permission = is_method_admin
    has_change_permission = is_method_admin
    has_delete_permission = is_method_admin


class AccuracyUnitsDomAdmin(ReferenceTableAdmin):
    class Meta:
        model = models.AccuracyUnitsDom

    list_display = (
        'accuracy_units', 'accuracy_units_description', 'data_entry_name',
        'data_entry_date', 'update_name', 'update_date'
    )
    readonly_fields = (
        'data_entry_name', 'data_entry_date', 'update_name', 'update_date'
    )
    fieldsets = (
        (None, {
            'fields': (
                'accuracy_units',
                'accuracy_units_description',
                ('data_entry_name', 'data_entry_date'),
                ('update_name', 'update_date'),
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        self.audit_instance(request.user.username, obj)
        return super(AccuracyUnitsDomAdmin, self).save_model(request, obj, form, change)


class AnalyteCodeRelAdmin(UserTimestampMixin, admin.TabularInline):
    model = models.AnalyteCodeRel
    extra = 0
    fields = ('analyte_name', 'preferred') + UserTimestampMixin.fields

    def save_model(self, request, obj, form, change):
        self.audit_instance(request, obj, change)
        return super(AnalyteCodeRelAdmin, self).save_model(request, obj, form, change)


class AnalyteRefAdmin(UserTimestampMixin, ReferenceTableAdmin):
    class Meta:
        model = models.AnalyteRef

    inlines = (AnalyteCodeRelAdmin,)
    list_display = ('analyte_code', 'analyte_type', 'analyte_cbr')
    fields = (
        'analyte_code', 'analyte_type', 'analyte_cbr', 'usgs_pcode',
        'analyte_code_cbr',
        # These two are in the database but not in the APEX UI:
        #'cbr_analyte_category', 'cbr_analyte_intro'
    ) + UserTimestampMixin.fields

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


method_admin.register(models.AccuracyUnitsDom, AccuracyUnitsDomAdmin)
method_admin.register(models.AnalyteRef, AnalyteRefAdmin)
