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
    inlines = (IngredientInline,)
    empty_value_display = 'Пусто'

    def get_favorites(self, obj):
        return obj.favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        ingredients_list = [
            f"{ingredient.ingredient.name} - "
            f"{ingredient.amount} {ingredient.ingredient.measurement_unit}"
            for ingredient in obj.ingredients.through.objects.filter(
                recipe=obj
            )
        ]
        return mark_safe('<br>'.join(ingredients_list))
    get_ingredients.short_description = 'Ингредиенты'

    def get_image(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" width="50" height="50" />'
        )
    get_image.short_description = 'Изображение'

    def get_tags(self, obj):
        return ', '.join([
            tag.name for tag in obj.tags.all()
        ])
    get_tags.short_description = 'Теги'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    empty_value_display = 'Пусто'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = 'Пусто'

    def display_color(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px;'
            'background-color: {};"></div>',
            obj.color
        )
    display_color.short_description = 'Цвет'


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


class HasSubscriptionsFilter(admin.SimpleListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(following__isnull=False).distinct()


class HasFollowersFilter(admin.SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(follower__isnull=False).distinct()


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
    list_filter = (HasFollowersFilter, HasSubscriptionsFilter)
    ordering = ('username', )
    empty_value_display = 'Пусто'

    def get_subscriptions_count(self, obj):
        return obj.following.count()
    get_subscriptions_count.short_description = 'Число подписок'

    def get_followers_count(self, obj):
        return obj.follower.count()
    get_followers_count.short_description = 'Число подписчиков'

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    get_recipes_count.short_description = 'Число рецептов'
