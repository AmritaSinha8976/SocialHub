"""
Management command: python manage.py delete_expired_stories
Deletes stories older than 24 hours.
Suitable for a cron job: run every hour.

Cron example:
  0 * * * * /path/to/venv/bin/python /path/to/manage.py delete_expired_stories
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from stories.models import Story


class Command(BaseCommand):
    help = 'Deletes stories that have passed their 24-hour expiry.'

    def handle(self, *args, **options):
        expired = Story.objects.filter(expires_at__lt=timezone.now())
        count   = expired.count()
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired stories.'))
