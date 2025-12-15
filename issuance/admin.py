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


from django.contrib import admin

# Register your models here.
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from issuance.models import Configuration, IssuedCredential


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "tag")
    search_fields = ("key", "tag")


@admin.register(IssuedCredential)
class IssuedCredentialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vc_type",
        "credential_type",
        "organization_identifier",
        "employee_id",
        "subject_id",
        "status",
        "credential_id",
        "creation_at",
        "update_at",
    )
    search_fields = ("vc_type", "subject_id", "organization_identifier", "status", "credential_type", "employee_id")
    list_filter = ("organization_identifier", "status", "credential_type", "employee_id")

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
