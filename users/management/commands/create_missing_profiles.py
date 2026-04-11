"""
Management command: python manage.py create_missing_profiles
Backfills Profile rows for any User that doesn't have one.
Run this once after the initial migration if you created users before
the users app migrations had been applied.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates missing Profile rows for existing users.'

    def handle(self, *args, **options):
        users_without_profiles = [
            u for u in User.objects.all()
            if not Profile.objects.filter(user=u).exists()
        ]

        if not users_without_profiles:
            self.stdout.write(self.style.SUCCESS('All users already have profiles. Nothing to do.'))
            return

        created = 0
        for user in users_without_profiles:
            Profile.objects.create(user=user)
            created += 1
            self.stdout.write(f'  Created profile for: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'\nDone. Created {created} missing profile(s).'))
