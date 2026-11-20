import os

from .base import *

DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = [
    h for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h
]