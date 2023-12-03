import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/tags.json', encoding='utf-8') as data_file_tags:
            tags_data = json.loads(data_file_tags.read())
            tag_objects = [Tag(**data) for data in tags_data]
            Tag.objects.bulk_create(tag_objects, batch_size=1000)
