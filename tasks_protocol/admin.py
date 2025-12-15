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


# Add this code in any Django app's admin.py
# Works for all Task Statuses; you can filter them in line 12.

from django.contrib import admin
from django.contrib import messages

from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from .service import push_to_queue


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = push_to_queue(queryset)
    messages.info(request, msg)


retry_celery_task_admin_action.short_description = "Retry Task"  # type: ignore


class CustomTaskResultAdmin(TaskResultAdmin):
    actions = [retry_celery_task_admin_action]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)
