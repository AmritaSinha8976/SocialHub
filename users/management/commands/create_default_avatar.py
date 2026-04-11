"""
Management command: python manage.py create_default_avatar
Creates a simple default avatar PNG in media/profile_pics/
so new users always have a fallback image.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates the default profile picture if it does not exist.'

    def handle(self, *args, **options):
        dest_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pics')
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, 'default.png')

        if os.path.exists(dest):
            self.stdout.write(self.style.WARNING(f'Default avatar already exists: {dest}'))
            return

        # Generate a minimal 80×80 grey PNG using Pillow
        try:
            from PIL import Image, ImageDraw
            size = 80
            img = Image.new('RGB', (size, size), color=(200, 200, 200))
            draw = ImageDraw.Draw(img)
            # Draw a simple silhouette circle + body shape
            head_r = 22
            cx, cy = size // 2, size // 2
            draw.ellipse(
                [cx - head_r, cy - head_r - 8, cx + head_r, cy + head_r - 8],
                fill=(150, 150, 150)
            )
            draw.ellipse(
                [cx - 30, cy + 18, cx + 30, cy + 70],
                fill=(150, 150, 150)
            )
            img.save(dest)
            self.stdout.write(self.style.SUCCESS(f'Default avatar created at: {dest}'))
        except ImportError:
            self.stdout.write(self.style.ERROR('Pillow not installed. Run: pip install Pillow'))
