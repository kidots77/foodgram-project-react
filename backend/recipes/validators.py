import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_username(value):
    pattern = r'^[\w.@+-]+$'

    invalid_characters = [
        char for char in value if not re.match(pattern, char)
    ]
    if invalid_characters:
        raise ValidationError(
            _('Логин содержит недопустимые символы: %(value)s'),
            code='invalid',
            params={'value': ', '.join(invalid_characters)},
        )
