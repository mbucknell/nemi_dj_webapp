from django.contrib import admin

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


class MethodOnlineAdmin(AbstractMethodAdmin):
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


class MethodStgAdmin(AbstractMethodAdmin):
    class Meta:
        model = models.MethodStg

    def has_change_permission(self, request, obj=None):
        return obj is None


class MethodAdmin(AbstractMethodAdmin):
    class Meta:
        model = models.Method

    def has_change_permission(self, request, obj=None):
        return obj is None


method_admin.register(models.MethodOnline, MethodOnlineAdmin)
method_admin.register(models.MethodStg, MethodStgAdmin)
method_admin.register(models.Method, MethodAdmin)
