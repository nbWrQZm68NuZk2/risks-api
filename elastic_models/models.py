from contextlib import contextmanager

from django.core.exceptions import ValidationError
from django.db import models
from django_hstore import hstore
from django_hstore.fields import DictionaryField
from jsonfield.fields import JSONField

from elastic_models.helpers import list_of_strings_validator, alphanumeric_or_under_validator

NAME_MAX_LENGTH = 255


class Schema(models.Model):
    """ Defines elastic model """

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    name_plural = models.CharField(max_length=NAME_MAX_LENGTH, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_hstore_field_definitions(self):
        return [definition.get_hstore_definition() for definition in self.field_definitions.all()]

    def __str__(self):
        return self.name.title()

    def _adjust_names(self):
        self.name = self.name.lower()

        if not self.name_plural:
            self.name_plural = '{}s'.format(self.name)
        self.name_plural = self.name_plural.lower()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self._adjust_names()
        super().save(force_insert, force_update, using, update_fields)


class FieldDefinition(models.Model):
    """" Defines fields of an elastic model """

    class Meta:
        unique_together = (('schema', 'name'), )
        ordering = 'id',

    NUMBER = 'number'
    TEXT = 'text'
    ENUM = 'enum'
    DATE = 'date'

    TYPE_CHOICES = (
        (NUMBER, 'Number'),
        (TEXT, 'Text'),
        (ENUM, 'Enum'),
        (DATE, 'Date'),
    )

    schema = models.ForeignKey('Schema', related_name='field_definitions')

    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    name = models.CharField(max_length=NAME_MAX_LENGTH, validators=[alphanumeric_or_under_validator, ])
    label = models.CharField(max_length=NAME_MAX_LENGTH, blank=True)
    blank = models.BooleanField(default=False)
    choices = JSONField(blank=True, validators=[list_of_strings_validator, ], default=list)

    def __str__(self):
        return self.name.title()

    def clean(self):
        if self.type == self.ENUM and not self.choices:
            raise ValidationError('Choices are required for Enum type')

        if self.type != self.ENUM and self.choices:
            raise ValidationError('Choices are allowed only for Enum type')

    TYPE_TO_DJANGO_CLASS_MAPPING = {
        NUMBER: 'IntegerField',
        TEXT: 'TextField',
        ENUM: 'CharField',
        DATE: 'DateField',
    }

    def get_hstore_definition(self):
        """ Return field definition compatibile with django_hstore.fields.DictionaryField """

        definiton = {
            'class': self.TYPE_TO_DJANGO_CLASS_MAPPING[self.type],
            'name': self.name,
            'kwargs': {
                'blank': self.blank,
            }
        }
        if self.choices:
            definiton['kwargs']['choices'] = [[value, value] for value in self.choices]

        if self.blank:
            if self.type in(self.NUMBER, self.DATE):
                definiton['kwargs']['null'] = True

        return definiton

    def _adjust_names(self):
        self.name = self.name.lower()

        if not self.label:
            self.label = self.name.title()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self._adjust_names()
        self.schema.instances.all().delete()
        super().save(force_insert, force_update, using, update_fields)


class Instance(models.Model):
    """ Stores instances of multiple elastic models """

    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name='instances')
    data = DictionaryField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = hstore.HStoreManager()

    @classmethod
    def load_schema(cls, schema=None):
        """ Build model fields referencing hstore keys based on schema """

        hstore_dictionary_field = cls._meta.get_field('data')

        if schema is not None:
            hstore_dictionary_field.reload_schema(schema.get_hstore_field_definitions())
        else:
            hstore_dictionary_field.reload_schema(None)


@contextmanager
def schema_loaded(schema):
    """ Execute code block with given schema loaded """
    Instance.load_schema(schema)
    yield
    Instance.load_schema(None)
