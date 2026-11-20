import os

from dotenv import load_dotenv

from .base import *
from .base import BASE_DIR

load_dotenv(BASE_DIR / '.env')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']