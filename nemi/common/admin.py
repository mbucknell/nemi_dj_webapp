from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Case, Count, Q, When
from django.forms.models import BaseInlineFormSet
from django.template.defaultfilters import slugify
import PyPDF2

from django_object_actions import (
    DjangoObjectActions, takes_instance_or_queryset)

from nemi_project.admin import method_admin
from common import models


class ReadOnlyMixin:
    """
    Since the admin interface does not include read-only functionality, here
    we provide a workaround that may be used with the change view on any
    `ModelAdmin`.

    This mixin will make each field readonly, disable save
    buttons in the template, and disable the save-on-POST.
    """
    def get_readonly_fields(self, request, obj=None):
        # Blunt force, return every field on the model.
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        # This is just to enable the change view in the interface.
        # The rest of the class disables actual change actions.
        # Currently, only admin.
        return request.user.is_superuser

    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = {
            'show_save': False,
            'show_delete_link': False,
            'show_save_as_new': False,
            'show_save_and_add_another': False,
            'show_save_and_continue': False,
        }
        context.update(extra_context or {})

        return super(ReadOnlyMixin, self).change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=context
        )

    def save_model(self, request, obj, form, change):
        raise PermissionDenied


class PDFFileWidget(admin.widgets.AdminFileWidget):
    template_name = 'common/widgets/pdf_file_input.html'


class PDFFileField(forms.FileField):
    widget = PDFFileWidget

    def clean(self, value, initial=None):
        value = super(PDFFileField, self).clean(value)

        # To validate the PDF, try to read it with PyPDF2.
        if value:
            try:
                PyPDF2.PdfFileReader(value)
            except PyPDF2.utils.PdfReadError:
                raise ValidationError('Please upload a valid PDF file.')

        return value


class RevisionFile:
    def __init__(self, revision, stage):
        self.revision = revision
        self.view_name = {
            'live': 'revision-pdf',
            'online': 'revision-pdf-online',
            'stg': 'revision-pdf-staging',
        }[stage]

    @property
    def url(self):
        return reverse(self.view_name, args=[self.revision.pk])


class AbstractRevisionForm(forms.ModelForm):
    pdf_file = PDFFileField(required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        revision = kwargs.get('instance')
        if revision and revision.method_pdf:
            initial['pdf_file'] = RevisionFile(revision, self.STAGE)
        kwargs['initial'] = initial
        super(AbstractRevisionForm, self).__init__(*args, **kwargs)

    def clean_pdf_file(self):
        if self.cleaned_data['pdf_file']:
            # To validate the PDF, try to read it with PyPDF2.
            try:
                PyPDF2.PdfFileReader(self.cleaned_data['pdf_file'])
            except PyPDF2.utils.PdfReadError:
                raise ValidationError('Please upload a valid PDF file.')
        return self.cleaned_data['pdf_file']

    def save(self, commit=True):
        instance = super(AbstractRevisionForm, self).save(commit=False)

        if self.cleaned_data['pdf_file']:
            self.cleaned_data['pdf_file'].seek(0)
            instance.method_pdf = self.cleaned_data['pdf_file'].read()
            instance.mimetype = 'application/pdf'

        if commit:
            instance.save()

        return instance


class RevisionOnlineForm(AbstractRevisionForm):
    STAGE = 'online'
    class Meta:
        model = models.RevisionJoinOnline
        fields = (
            'revision_flag', 'revision_information', 'source_citation',
            'pdf_file',
            #'reviewer_name'
        )


class RevisionStgForm(AbstractRevisionForm):
    STAGE = 'stg'
    class Meta:
        model = models.RevisionJoinStg
        fields = (
            'revision_flag', 'revision_information', 'source_citation',
            'pdf_file',
            #'reviewer_name'
        )


class RevisionInlineFormSet(BaseInlineFormSet):
    fieldsets = (
        (None, {
            'fields': ('revision_flag', 'revision_information', 'source_citation')
        })
    )

    def clean(self):
        super(RevisionInlineFormSet, self).clean()

        # If more than one revision has `revision_flag` set, error.
        if sum(f.cleaned_data.get('revision_flag') or 0 for f in self.forms) > 1:
            msg = 'There may not be more than one active revision per method.'
            raise ValidationError(msg)


class AbstractRevisionInline(ReadOnlyMixin, admin.TabularInline):
    extra = 0
    formset = RevisionInlineFormSet
    class Meta:
        abstract = True


class AbstractEditableRevisionInline(AbstractRevisionInline):
    class Meta:
        abstract = True

    def pdf_file(self):
        # If we have a method_pdf, use the revision name as the PDF label.
        return '%s.pdf' % self.revision_information if self.method_pdf else None

    def save_model(self, request, obj, form, change):
        if not change:
            obj.insert_person_name = request.user.username
        obj.last_update_person_name = request.user.username
        return super(AbstractEditableRevisionInline, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # Owners can edit any field when in the "online" tables.
        # if obj and obj.insert_person_name == request.user.username:
        #     return ()
        # return super(AbstractEditableRevisionInline, self).get_readonly_fields(request, obj=obj)

        # For now, allow any admin to edit the online and staging tables.
        return ()

    def has_add_permission(self, request):
        # As an inline, we defer to the parent permissions
        return True

    def has_change_permission(self, request, obj=None):
        # As an inline, we defer to the parent permissions
        return True


class RevisionOnlineAdmin(AbstractEditableRevisionInline):
    model = models.RevisionJoinOnline
    form = RevisionOnlineForm


class RevisionStgAdmin(AbstractEditableRevisionInline):
    model = models.RevisionJoinStg
    form = RevisionStgForm


class RevisionAdmin(AbstractRevisionInline):
    model = models.RevisionJoin
    readonly_fields = (
        'mimetype', 'revision_flag', 'revision_information', 'insert_date',
        'insert_person_name', 'last_update_date', 'last_update_person_name',
        'pdf_insert_person', 'pdf_insert_date', 'source_citation',
        'date_loaded', 'revision_pdf_url')

    def revision_pdf_url(self, obj):
        if not obj.pk:
            return ''
        return '<a href="%s">Download PDF</a>' % reverse('revision-pdf',
                                                         args=[obj.pk])

    revision_pdf_url.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


class ActiveRevisionCountFilter(admin.SimpleListFilter):
    title = 'active revision count'
    parameter_name = 'active_revision_count'

    def lookups(self, request, model_admin):
        return (
            (0, 'None'),
            (1, 'One'),
            (2, 'More than one')
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            return queryset

        if value > 1:
            return queryset.filter(active_revision_count__gt=1)

        return queryset.filter(active_revision_count=value)


def list_q_filter(label, q_object):
    class ListQFilter(admin.SimpleListFilter):
        title = label
        parameter_name = slugify(label)

        def lookups(self, request, model_admin):
            return (
                ('1', 'Yes'),
                ('0', 'No'),
            )

        def queryset(self, request, queryset):
            if self.value() == '1':
                return queryset.filter(q_object)
            elif self.value() == '0':
                return queryset.filter(~q_object)

            return queryset

    return ListQFilter


class AbstractMethodAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    list_display = (
        'method_official_name', 'insert_date', 'last_update_date',
        'approved', 'approved_date', 'active_revision_count'
    )
    list_filter = (
        ActiveRevisionCountFilter,
        list_q_filter(
            'active revision has PDF',
            Q(revisions__revision_flag=True) and Q(
                revisions__method_pdf__isnull=False)
        ),
        'approved', 'insert_date', 'approved_date', 'insert_person_name'
    )
    fieldsets = (
        ('General Fields', {
            #'classes': ('collapse',),
            'fields': (
                'source_method_identifier', 'method_descriptive_name',
                'method_type', 'method_subcategory',
                'method_source', 'source_citation', 'brief_method_summary',
                'media_name', 'method_official_name', 'instrumentation',
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
                'assumptions_comments',
            )
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(AbstractMethodAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)

        # Make fields required here rather than in DB models, so the
        # statistical method forms' functionality won't be impacted.
        if db_field.name in ('media_name', 'method_source', 'method_descriptive_name'):
            field.required = True

        return field

    def get_queryset(self, request):
        queryset = super(AbstractMethodAdmin, self).get_queryset(request)

        # Add annotation for the count of active revisions per method.
        queryset = queryset.annotate(
            active_revision_count=Count(Case(When(
                revisions__revision_flag=True,
                then=1
            )))
        )

        return queryset

    def active_revision_count(self, obj):
        return obj.active_revision_count

    def has_module_permission(self, request):
        # For now, only admins have access
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MethodOnlineAdmin(DjangoObjectActions, AbstractMethodAdmin):
    class Meta:
        model = models.MethodOnline

    list_filter = ('ready_for_review',) + AbstractMethodAdmin.list_filter
    inlines = (RevisionOnlineAdmin,)
    actions = ('submit_for_review',)
    change_actions = actions
    fieldsets = (
        ('Submission-Specific Fields', {
            'fields': (
                ('no_analyte_flag',),
                ('ready_for_review', 'delete_after_load'),
                ('comments',),
            )
        }),
    ) + AbstractMethodAdmin.fieldsets

    def has_add_permission(self, request):
        # For now, only admins have acesss.
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Users may edit their own submissions, if it hasn't already been
        # submitted for review.
        # Currently, assume only admin users use the system.
        return request.user.is_superuser

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

    def get_readonly_fields(self, request, obj=None):
        # Owners can edit any field when in the "online" tables.
        if obj and obj.insert_person_name == request.user.username:
            return ()
        return super(MethodOnlineAdmin, self).get_readonly_fields(request, obj=obj)


class MethodStgAdmin(DjangoObjectActions, AbstractMethodAdmin):
    class Meta:
        model = models.MethodStg

    inlines = (RevisionStgAdmin,)
    actions = ('publish', 'archive')
    change_actions = actions
    fieldsets = (
        ('Review-Specific Fields', {
            'fields': (
                ('no_analyte_flag',),
            )
        }),
    ) + AbstractMethodAdmin.fieldsets

    @takes_instance_or_queryset
    def publish(self, request, queryset):
        rows_updated = queryset.update(approved='Y')
        self.message_user(request, 'published %d method%s' % (
            rows_updated, 's' if rows_updated > 1 else ''))

    publish.label = 'Publish'
    publish.short_description = 'Publish the selected methods'

    @takes_instance_or_queryset
    def archive(self, request, queryset):
        method_ids = queryset.values_list('method_id', flat=True)
        try:
            cursor = connection.cursor()
            for method_id in method_ids:
                cursor.callproc(
                    'archive_method', [
                        method_id,
                        'Y',  # DELETE_FLAG - remove from staging and production
                        'Y',  # PUBLIC_FLAG - method should be public
                    ]
                )
        finally:
            cursor.close()

        rows_updated = len(method_ids)
        self.message_user(request, 'archived %d method%s' % (
            rows_updated, 's' if rows_updated > 1 else ''))

    archive.label = 'Archive'
    archive.short_description = 'Archive the selected methods'

    def has_change_permission(self, request, obj=None):
        # Admin may only edit staging methods
        return request.user.is_superuser


class MethodAdmin(ReadOnlyMixin, AbstractMethodAdmin):
    class Meta:
        model = models.Method

    inlines = (RevisionAdmin,)


method_admin.register(models.MethodOnline, MethodOnlineAdmin)
method_admin.register(models.MethodStg, MethodStgAdmin)
method_admin.register(models.Method, MethodAdmin)
