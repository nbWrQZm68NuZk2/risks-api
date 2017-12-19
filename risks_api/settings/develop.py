from .defaults import *

DEBUG = True

DATABASES = {
    'default': {
        'HOST': 'risks-api-develop.cx497drbduxo.eu-central-1.rds.amazonaws.com',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'risks_api',
        'USER': 'risks_api',
        'PASSWORD': 'pR7cpfojTx8aB8',
    }
}

ALLOWED_HOSTS = ['0k1sug0ej1.execute-api.eu-central-1.amazonaws.com', ]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_LOCATION = 'static'
AWS_STORAGE_BUCKET_NAME = 'risks-api-dev'
