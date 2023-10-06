from django.contrib.auth import get_user_model

from recipes.models import Ingredient


User = get_user_model()


class IngredientSerializer(serializers.modelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
