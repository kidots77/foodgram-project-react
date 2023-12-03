import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            'data/ingredients.json', encoding='utf-8'
        ) as data_file_ingredients:
            ingredient_data = json.loads(data_file_ingredients.read())
            ingredient_objects = [
                Ingredient(**data) for data in ingredient_data
            ]
            Ingredient.objects.bulk_create(ingredient_objects, batch_size=1000)
