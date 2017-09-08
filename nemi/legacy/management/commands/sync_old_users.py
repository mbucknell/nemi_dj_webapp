"""
This command will read all users in the user_account table and create a
corresponding `django.contrib.auth` user, if the specified username does not
already exist. New accounts will have a random password assigned, and should
use the "forgot password" tool to create a new password.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from legacy import models


class Command(BaseCommand):
    help = 'Creates Django user accounts for each legacy account.'

    def handle(self, *args, **options):
        new_users = set()
        existing_users = set()
        for account in models.LegacyUserAccount.objects.all():
            user, created = User.objects.get_or_create(
                username=account.user_name,
                defaults={
                    'is_superuser': False,
                    'is_staff': False,
                    'is_active': True,
                    'first_name': account.first_name,
                    'last_name': account.last_name,
                    'email': account.email,
                    'last_login': account.last_login,
                },
            )
            if created:
                new_users.add(user)
                user.set_password(User.objects.make_random_password())
            else:
                existing_users.add(user)

        print('These %s users were added:' % len(new_users))
        for user in sorted(new_users, key=lambda u: u.username):
            print('\t'.join([
                user.username,
                user.first_name,
                user.last_name,
                user.email
            ]))

        print('These %s users already exist:' % len(existing_users))
        for user in sorted(existing_users, key=lambda u: u.username):
            print('\t'.join([
                user.username,
                user.first_name,
                user.last_name,
                user.email
            ]))
