from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
import re

NAME_REGULAR_EXPRESSION = re.compile(r'^\w+[\w\-\.: ]+$')


def greater_than_zero(value):
    """Checks if value is greater than zero"""
    if value <= 0:
        raise ValidationError("Value must be greater than zero.")


def positive(value):
    """Checks if value is greater than or equal to zero"""
    if value < 0:
        raise ValidationError("Value must be greater than or equal to zero.")


def validate_name(value):
    """Ensures that a string matches a regular expression and that the
    slugified version of a string is not the empty string"""
    if NAME_REGULAR_EXPRESSION.match(value) is None:
        msg = "This is not an acceptable name."
        raise ValidationError(msg)
    if slugify(value) == "":
        msg = "Name must contain some letters or numbers."
        raise ValidationError(msg)
