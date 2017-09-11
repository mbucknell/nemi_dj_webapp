# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import Group


def forwards_func(apps, schema_editor):
    # Create the permission groups corresponding to the original legacy
    # behavior. We will use these in a role-based manner, rather than add
    # low-level permissions to each group.
    Group.objects.bulk_create([
        # admin: can add/edit/delete any method
        Group(name='method_admin'),

        # data_entry: can edit own method
        Group(name='method_data_entry'),

        # can review methods where matches reviewer_name in method table
        Group(name='method_reviewer')
    ])


def reverse_func(apps, schema_editor):
    Group.objects.filter(
        name__in=['method_admin', 'method_data_entry', 'method_reviewer']
    ).delete()


class Migration(migrations.Migration):
    dependencies = []
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
