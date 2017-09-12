from django.contrib import admin
from django_object_actions import (
    DjangoObjectActions, takes_instance_or_queryset)

from nemi_project.admin import method_admin
from common import models


class AbstractMethodAdmin(admin.ModelAdmin):
    class Meta:
        fields = '__all__'
        abstract = True

    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date'
    )

    def get_queryset(self, request):
        queryset = super(AbstractMethodAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(insert_person_name=request.user.username)
        return queryset

    def has_module_permission(self, request):
        # All active users have method
        return request.user.is_active

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MethodOnlineAdmin(DjangoObjectActions, AbstractMethodAdmin):
    exclude = (
        'insert_person_name', 'insert_person_name2', 'insert_date',
        'last_update_date', 'last_update_person_name', 'approved',
        'approved_date', 'reviewer_name')
    actions = ('submit_for_review',)
    change_actions = actions

    class Meta:
        model = models.MethodOnline

    def has_add_permission(self, request):
        # Anyone may submit new methods for review
        return request.user.is_active

    def has_change_permission(self, request, obj=None):
        # Users may edit their own submissions, if it hasn't already been
        # submitted for review.
        return obj is None or (
            obj.insert_person_name == request.user.username and
            obj.ready_for_review == 'N')

    @takes_instance_or_queryset
    def submit_for_review(self, request, queryset):
        rows_updated = queryset.update(ready_for_review='Y')
        self.message_user(request, 'submitted %d method%s for review' % (
            rows_updated, 's' if rows_updated > 1 else ''))

    submit_for_review.label = 'Submit for review'
    submit_for_review.short_description = 'Submit method for review'

    def save_model(self, request, obj, form, change):
        # If adding a new instance, set `insert_person_name` to current user.
        if not change:
            obj.insert_person_name = request.user.username
        return super(MethodOnlineAdmin, self).save_model(request, obj, form, change)


class MethodStgAdmin(DjangoObjectActions, AbstractMethodAdmin):
    class Meta:
        model = models.MethodStg

    actions = ('publish',)
    change_actions = actions

    def has_change_permission(self, request, obj=None):
        return obj is None

    @takes_instance_or_queryset
    def publish(self, request, queryset):
        rows_updated = queryset.update(approved='Y')
        self.message_user(request, 'published %d method%s' % (
            rows_updated, 's' if rows_updated > 1 else ''))

    publish.label = 'Publish'
    publish.short_description = 'Publish the selected methods'


class MethodAdmin(AbstractMethodAdmin):
    class Meta:
        model = models.Method

    def has_change_permission(self, request, obj=None):
        return obj is None


method_admin.register(models.MethodOnline, MethodOnlineAdmin)
method_admin.register(models.MethodStg, MethodStgAdmin)
method_admin.register(models.Method, MethodAdmin)
