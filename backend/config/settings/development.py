import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-insecure-key-diganti-di-T0.5',
)