from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSer, ReadOnlyModelViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)

from recipes.models import Ingredient
from recipes.filters import IngredientSearchFilter
from api.serializers import IngredientSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    # filter_backends = [IngredientSearchFilter]
    # @action(detail=False, permission_classes=[IsAuthenticated])
    # def action(self, request):
    #     raise NotImplementedError(test)
