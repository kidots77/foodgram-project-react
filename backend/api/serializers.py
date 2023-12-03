from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as UserSrlz
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)
from recipes.models import User


class UserSerializer(UserSrlz):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class SubscribeListSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!'
            )
        if user == author:
            raise ValidationError(
                detail='Подписаться на самом себя невозможно!'
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10**10))
        serializer = RecipeShortSerializer(
            obj.recipes.all()[: limit], many=True, read_only=True
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredienttorecipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'tags': 'Такого тега не существует!'}
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не менее одной минуты!')
        return cooking_time

    @staticmethod
    def validate_unique_items(items, field_name):
        items_list = []
        for item in items:
            if item in items_list:
                raise serializers.ValidationError(
                    f'Ингредиент {item} не может повторяться!'
                )
            items_list.append(item)
        return items

    def validate(self, data):
        validated_data = super().validate(data)
        if 'ingredients' in validated_data:
            ingredients = validated_data['ingredients']
            if not ingredients:
                raise serializers.ValidationError(
                    'Нужен хотя бы один ингредиент!'
                )
            for ingredient in ingredients:
                if int(ingredient['amount']) <= 0:
                    raise serializers.ValidationError(
                        'Количество ингредиента должно быть больше 0!'
                    )
            validated_data['ingredients'] = self.validate_unique_items(
                ingredients, 'Ингредиенты'
            )

        if 'tags' in validated_data:
            tags = validated_data['tags']
            if not tags:
                raise serializers.ValidationError(
                    'Нужно выбрать как минимум 1 тег!'
                )
            validated_data['tags'] = self.validate_unique_items(tags, 'Теги')

        return validated_data

    def validate_image(self, image):
        if not image:
            raise ValidationError('Нужна картинка рецепта/блюда!')
        return image

    @staticmethod
    def create_ingredients(recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient=ingredient_data.pop('id'),
                amount=ingredient_data.pop('amount'),
                recipe=recipe,
            )for ingredient_data in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        print(validated_data)
        if (
            'tags' in validated_data.keys() and 'ingredients'
            in validated_data.keys()
        ):
            instance.tags.set(validated_data.pop('tags'))
            ingredients = validated_data.pop('ingredients')
        else:
            raise ValidationError('Теги и/или ингредиенты не указаны')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
