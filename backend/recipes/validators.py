import re

from django.core.exceptions import ValidationError

PATTERN = r'^[\w.@+-]+$'


def validate_username(username):
    invalid_characters = set(re.findall(r'[^\w.@+-]', username))
    if invalid_characters:
        raise ValidationError(
            f'Логин {username} некорректный. '
            'Логин может содержать только буквы, '
            'цифры и следущие знаки: @/./+/-/_'
            f'Текущий логин содержит недопустимые символы: '
            f'{invalid_characters}\n')
