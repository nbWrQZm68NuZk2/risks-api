import string

from django.core.exceptions import ValidationError


def list_of_strings_validator(value):
    """ Validates whether value is a list of strings """

    if not isinstance(value, list) or not all(map(lambda item: isinstance(item, str), value)):
        raise ValidationError('List of strings expected')

    if len(value) != len(set(value)):
        raise ValidationError('List items must be unique')


def alphanumeric_or_under_validator(value):
    allowed_characters = string.ascii_lowercase + '_'

    for character in value:
        if character not in allowed_characters:
            raise ValidationError('Value is invalid')
