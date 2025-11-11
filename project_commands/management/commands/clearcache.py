import os
from shutil import rmtree

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clear django cache (.cache)'

    def handle(self, *args, **options):
        if os.path.exists('.cache'):
            rmtree('.cache')
