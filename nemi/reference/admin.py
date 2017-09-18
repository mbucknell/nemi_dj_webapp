from datetime import datetime

from django.contrib import admin

from nemi_project.admin import method_admin

from . import models


class ReferenceTableAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    def is_method_admin(self, request, *args, **kwargs):
        if not hasattr(self, '_admin'):
            self._is_admin = request.user.groups.filter(
                name='method_admin').exists()
        return self._is_admin

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
        if change:
            obj.update_name = request.user.username
            obj.update_date = datetime.now()
        else:
            obj.data_entry_name = request.user.username
            obj.update_date = datetime.now()
        return super(AccuracyUnitsDomAdmin, self).save_model(request, obj, form, change)


method_admin.register(models.AccuracyUnitsDom, AccuracyUnitsDomAdmin)
