import re

from django.core.exceptions import ValidationError

PATTERN = r'^[\w.@+-]+$'


def validate_username(username):
    invalid_characters = set(re.findall(r'[^\w.@+-]', username))
    if invalid_characters:
        error_message = ('Введите корректный логин. Он может содержать только буквы, цифры и следущие знаки: @/./+/-/_'
                         'Текущий логин содержит недопустимые символы:\n')
        for index, char in enumerate(invalid_characters, start=1):
            if char != ' ':
                error_message += f"{index}. {char}\n"
            else:
                error_message += f"{index}. (пробел)\n"
        raise ValidationError(error_message)
