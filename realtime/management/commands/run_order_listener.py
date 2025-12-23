from django.core.management.base import BaseCommand
from realtime import listeners


class Command(BaseCommand):
    help = "Run Redis subscriber for order events"

    def handle(self, *args, **kwargs):
        listeners.main()
