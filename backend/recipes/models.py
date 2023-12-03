from colorfield.fields import ColorField
from django.db import models
from django.db.models import F, Q, UniqueConstraint
from django.core.validators import (
    RegexValidator
)

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
    )
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(), validate_username)
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta():
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        db_index=True,
        unique=True
    )
    color = ColorField(
        verbose_name='HEX-код',
        format='hex',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#[A-Fa-f0-9]{6})$",
                message='Вы ввели несуществующий цвет!',
            )
        ],
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег',
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    """ Модель Корзина покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'


class IngredientRecipe(models.Model):
    """ Ингридиенты рецепта. """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиента в рецепте'

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )
