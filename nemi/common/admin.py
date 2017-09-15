from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
import PyPDF2

from django_object_actions import (
    DjangoObjectActions, takes_instance_or_queryset)

from nemi_project.admin import method_admin
from common import models


class AbstractRevisionInline(admin.TabularInline):
    extra = 1
    class Meta:
        fields = '__all__'
        abstract = True


class RevisionOnlineForm(forms.ModelForm):
    class Meta:
        model = models.RevisionJoinOnline
        fields = (
            'revision_flag', 'revision_information', 'source_citation',
            'pdf_file',
            #'reviewer_name'
        )

    pdf_file = forms.FileField(required=False)

    def clean_pdf_file(self):
        if self.cleaned_data['pdf_file']:
            # To validate the PDF, try to read it with PyPDF2.
            try:
                PyPDF2.PdfFileReader(self.cleaned_data['pdf_file'])
            except PyPDF2.utils.PdfReadError:
                raise ValidationError('Please upload a valid PDF file.')

    def save(self, commit=True):
        instance = super(RevisionOnlineForm, self).save(commit=False)

        if self.cleaned_data['pdf_file']:
            instance.method_pdf = self.cleaned_data['pdf_file'].read()
            instance.mimetype = 'application/pdf'

        if commit:
            instance.save()

        return instance


class RevisionInlineFormSet(BaseInlineFormSet):
    class Meta:
        fields = '__all__'

    def clean(self):
        super(RevisionInlineFormSet, self).clean()

        # If more than one revision has `revision_flag` set, error.
        if sum(f.cleaned_data.get('revision_flag') or 0 for f in self.forms) > 1:
            msg = 'There may not be more than one active revision per method.'
            raise ValidationError(msg)


class RevisionOnlineAdmin(AbstractRevisionInline):
    model = models.RevisionJoinOnline
    form = RevisionOnlineForm
    formset = RevisionInlineFormSet

    def pdf_file(self):
        # If we have a method_pdf, use the revision name as the PDF label.
        print('%s.pdf' % self.revision_information if self.method_pdf else None)
        return '%s.pdf' % self.revision_information if self.method_pdf else None

    def save_model(self, request, obj, form, change):
        if not change:
            obj.insert_person_name = request.user.username
        obj.last_update_person_name = request.user.username
        return super(RevisionOnlineAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # As an inline, we defer to the parent permissions
        return True

    def has_change_permission(self, request, obj=None):
        # As an inline, we defer to the parent permissions
        return True


class RevisionStgAdmin(AbstractRevisionInline):
    model = models.RevisionJoinStg


class RevisionAdmin(AbstractRevisionInline):
    model = models.RevisionJoin


class AbstractMethodAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date'
    )
    fieldsets = (
        ('General Fields', {
            #'classes': ('collapse',),
            'fields': (
                'source_method_identifier', 'method_descriptive_name',
                'method_type', 'method_subcategory', 'no_analyte_flag',
                'method_source', 'brief_method_summary', 'media_name',
                'method_official_name', 'instrumentation',
                'waterbody_type', 'scope_and_application', 'dl_type',
                'dl_note', 'applicable_conc_range', 'conc_range_units',
                'interferences', 'precision_descriptor_notes',
                'qc_requirements', 'sample_handling', 'max_holding_time',
                'sample_prep_methods', 'relative_cost',
                'link_to_full_method', 'regs_only', 'reviewer_name',
            ),
        }),
        ('CBR-only fields', {
            'fields': (('rapidity', 'screening', 'cbr_only'),)
        }),
        ('Greenness profile fields', {
            'fields': (
                ('collected_sample_amt_ml', 'collected_sample_amt_g'),
                ('analysis_amt_ml', 'analysis_amt_g'),
                'liquid_sample_flag', 'ph_of_analytical_sample', 'calc_waste_amt',
                'quality_review_id', 'pbt', 'toxic', 'corrosive', 'waste',
                'assumptions_comments', 'matrix', 'technique', 'etv_link',
                'sam_complexity', 'level_of_training',
                'media_emphasized_note', 'media_subcategory', 'notes'
            )
        }),
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
    class Meta:
        model = models.MethodOnline

    inlines = (RevisionOnlineAdmin,)
    actions = ('submit_for_review',)
    change_actions = actions
    fieldsets = (
        ('Submission-Specific Fields', {
            'fields': (
                ('ready_for_review', 'delete_after_load'),
                ('source_citation',),
                ('comments',),
            )
        }),
    ) + AbstractMethodAdmin.fieldsets

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

    inlines = (RevisionStgAdmin,)
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

    inlines = (RevisionAdmin,)

    def has_change_permission(self, request, obj=None):
        return obj is None


method_admin.register(models.MethodOnline, MethodOnlineAdmin)
method_admin.register(models.MethodStg, MethodStgAdmin)
method_admin.register(models.Method, MethodAdmin)
