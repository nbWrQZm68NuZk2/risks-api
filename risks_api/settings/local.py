from .defaults import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'risks_api',
        'USER': 'uszywieloryba',
        'PASSWORD': '',
    }
}
