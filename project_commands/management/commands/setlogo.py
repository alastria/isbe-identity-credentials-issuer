
import os

from project import settings
import sentry_sdk
from django.core.management.base import BaseCommand

from project.services.ipfs_service import IPFSService


class Command(BaseCommand):
    help = "Upload logo to IPFS Command"

    def handle(self, *args, **options):

        path_logo = os.path.join(settings.BASE_DIR, "static/images/backend_template_logo_128.png")
        if not os.path.exists(path_logo):
            self.stderr.write(self.style.ERROR(f"No existe path logo {path_logo}"))
            return
        url = IPFSService.upload_file(path_logo)
        self.stdout.write(self.style.SUCCESS(f"Logo successfully uploaded to IPFS. URL = {url}"))
        return
