from typing import Any
from django.core.management.base import BaseCommand, CommandError
from strategy.models import Strategy

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
        Strategy.objects.create(
            title='个人免费版',
            price=0,
            projects=3,
            member=3,
            space=20,
            uploda=5,
        )