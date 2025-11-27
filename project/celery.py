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


from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from .settings import CELERY_BROKER_URL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project", broker=os.environ.get(CELERY_BROKER_URL))
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
