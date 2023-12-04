import re

from django.core.exceptions import ValidationError

PATTERN = r'^[\w.@+-]+$'

def validate_username(username):
    invalid_characters = re.findall(r'[^\w.@+-]', username)
    if invalid_characters:
        error_message = "Логин содержит недопустимые символы: \n"
        for index, char in enumerate(invalid_characters, start=1):
            error_message += f"{index}. {char}\n"
        raise ValidationError(error_message)