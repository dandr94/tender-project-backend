from django.core.management.base import BaseCommand

from settings.settings import BASE_DIR
from ...models import Category
import json
from django.db import transaction

file_path = BASE_DIR / 'api' / 'management' / 'cpv_codes' / 'cpv_codes.json'


class Command(BaseCommand):
    help = 'Import CPV codes to Database from JSON file'

    def handle(self, *args, **options):
        with open(file_path, 'r') as file:
            data = json.load(file)

        with transaction.atomic():

            for item in data:
                code = item.get('code')
                name = item.get('name')
                parent_code = item.get('parent')

                parent_category = None

                if parent_code:
                    parent_category = Category.objects.filter(code=parent_code).first()

                category = Category(
                    code=code,
                    name=name,
                    parent=parent_category
                )

                category.save()
                self.stdout.write(self.style.SUCCESS(f"Category: {code} - {name} successfully saved to database!"))
