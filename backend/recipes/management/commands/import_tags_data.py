import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/tags.json', encoding='utf-8') as data_file_tags:
            tags_data = json.loads(data_file_tags.read())
            Tag.objects.bulk_create(
                Tag(**data) for data in tags_data
            )
