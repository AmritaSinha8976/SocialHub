"""
Auto-select settings based on DJANGO_ENV environment variable.
Defaults to development if not set.
"""
import os

env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
