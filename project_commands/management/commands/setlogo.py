# Copyright (c) 2025 Comunidad de Madrid & Alastria
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
# [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0 "http://www.apache.org/licenses/license-2.0")
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
