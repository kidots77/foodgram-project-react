from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    User
)


admin.site.unregister(Group)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'cooking_time',
        'get_favorites',
        'get_ingredients',
        'get_image',
        'get_tags',
    )
    search_fields = (
        'name',
        'author',
        'tags'
    )
    list_filter = ('author', 'tags')
    inlines = (IngredientInline, )
    empty_value_display = 'Пусто'

    @admin.display(description='Избранное')
    def get_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe('<br>'.join(
            f'{ingredient_item.ingredient.name} - '
            f'{ingredient_item.amount} '
            f'{ingredient_item.ingredient.measurement_unit}'
            for ingredient_item in recipe.ingredienttorecipe.all()
        ))

    @admin.display(description='Изображение')
    def get_image(self, recipe):
        return mark_safe(
            f'<img src="{recipe.image.url}" width="50" height="50" />'
        )

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe(
            '<br>'.join(tag.name for tag in recipe.tags.all())
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    empty_value_display = 'Пусто'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'display_color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = 'Пусто'

    @admin.display(description='Цвет')
    def display_color(self, tag):
        return format_html(
            '<div style="width: 30px; height: 30px;'
            'background-color: {};"></div>',
            tag.color
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = 'Пусто'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = 'Пусто'


class SubscriptionsFollowersFilter(admin.SimpleListFilter):
    title = 'Подписчики и подписки'
    parameter_name = 'subscriptions_followers'

    def lookups(self, request, model_admin):
        return (
            ('has_subscriptions', 'Есть подписки'),
            ('has_followers', 'Есть подписчики'),
        )

    def queryset(self, request, users):
        value = self.value()
        if value == 'has_subscriptions':
            return users.filter(following__isnull=False).exists()
        if value == 'has_followers':
            return users.filter(follower__isnull=False).exists()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_subscriptions_count',
        'get_followers_count',
        'get_recipes_count',
    )
    search_fields = ('username', 'email', )
    list_filter = (SubscriptionsFollowersFilter,)
    ordering = ('username', )
    empty_value_display = 'Пусто'

    @admin.display(description='Подписки')
    def get_subscriptions_count(self, user):
        return user.following.count()

    @admin.display(description='Подписчики')
    def get_followers_count(self, user):
        return user.follower.count()

    @admin.display(description='Рецепты')
    def get_recipes_count(self, user):
        return user.recipes.count()
