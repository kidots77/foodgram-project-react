from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (
    status,
    viewsets,
    decorators,
    permissions,
    response,
    exceptions
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Follow, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly, MePermission
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeListSerializer,
    TagSerializer,
    UserSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Список ингредиентов для покупки:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @decorators.action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @decorators.action(
        detail=True,
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST' or request.method == 'GET':
            context = {'request': request}
            if Recipe.objects.filter(id=pk).exists():
                recipe = Recipe.objects.get(id=pk)
            else:
                raise exceptions.ValidationError(
                    'Указанного рецепта не существует!'
                )
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = ShoppingCartSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=request.user.id, recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                ShoppingCart.objects.filter(
                    user=request.user.id, recipe=get_object_or_404(
                        Recipe, id=pk
                    )
                ).delete()
            else:
                raise exceptions.ValidationError(
                    'Указанного рецепта нет в вашем списке покупок!'
                )
            return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            context = {"request": request}
            if Recipe.objects.filter(id=pk).exists():
                recipe = Recipe.objects.get(id=pk)
            else:
                raise exceptions.ValidationError('Такого рецепта нет!')
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = FavoriteSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if Favorite.objects.filter(
                user=request.user, recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                Favorite.objects.filter(
                    user=request.user, recipe=get_object_or_404(Recipe, id=pk)
                ).delete()
            else:
                raise exceptions.ValidationError(
                    'Этого рецепта нет в вашем списке избранного!'
                )
            return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (MePermission, )

    @decorators.action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE' and Follow.objects.filter(
            user=user, author=author
        ).exists():
            Follow.objects.filter(user=user, author=author).delete()
        else:
            raise exceptions.ValidationError(
                'Вы не подписаны на этого пользователя!'
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False, permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
