
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
        "organization_identity",
        "subject_id",
        "status",
        "credential_id",
        "creation_at",
        "update_at",
    )
    search_fields = ("vc_type", "subject_id", "organization_identity", "status")
    list_filter = ("organization_identity", "status", "creation_at")

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
