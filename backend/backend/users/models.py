from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ
# ПЕРЕПРОВЕРЬ ВСЕ


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        # validators=[
        #     RegexValidator(r'^[\w.@+-]+\Z')
        # ]
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False
    )

    first_name = models.CharField(
        max_length=150,
        unique=True,
        blank=False
    )

    last_name = models.CharField(
        max_length=150,
        unique=True,
        blank=False
    )

    password = models.CharField(
        max_length=150,
        blank=False,
        # validators=[
        #     RegexValidator(r'^[\w.@+-]+\Z')
        # ]
    )

    class Meta:
        ordering = ('username', )

    def __str__(self):
        return self.username