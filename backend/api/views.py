from django.db.models import Sum
from django.http.response import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (
    status,
    viewsets,
    permissions,
    response,
    exceptions
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework.permissions import IsAuthenticated, AllowAny

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from .shoppingcartmessage import send_message
from recipes.models import Follow, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import Page6Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    SubscribeListSerializer,
    TagSerializer,
    UserSerializer,
    RecipeShortSerializer
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
    pagination_class = Page6Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        else:
            return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            raise exceptions.ValidationError(
                'Указанного рецепта не существует!'
            )
        if model.objects.filter(user=user, recipe__id=pk).exists():
            raise exceptions.ValidationError(
                'Вы уже добавили этот рецепт'
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        if not model.objects.filter(
            user=user.id, recipe=get_object_or_404(Recipe, id=pk)
        ).exists():
            if model == ShoppingCart:
                raise exceptions.ValidationError(
                    'Указанного рецепта нет в вашем списке покупок!'
                )
            else:
                raise exceptions.ValidationError(
                    'Этого рецепта нет в вашем списке избранного!'
                )
        model.objects.filter(user=user, recipe__id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        user_shopping_cart_items = ShoppingCart.objects.filter(
            user=User.objects.get(username=user.username)
        )
        user_recipes_in_cart = [
            item.recipe for item in user_shopping_cart_items
        ]
        shopping_list = send_message(ingredients, user_recipes_in_cart)
        filename = f'{user.username}_shopping_list.txt'
        response = FileResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = Page6Pagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def me(self, request):
        return Response(
            UserSerializer(request.user, context={'request': request}).data
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
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
        else:
            if Follow.objects.filter(
                user=user, author=author
            ).exists():
                Follow.objects.filter(user=user, author=author).delete()
            else:
                raise exceptions.ValidationError(
                    'Вы не подписаны на этого пользователя!'
                )
            return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
