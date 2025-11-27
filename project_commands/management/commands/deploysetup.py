
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from issuance.models import (
    CONFIG_KEY_API_VERSION,
    CONFIG_KEY_APP,
    CONFIG_KEY_INSTANCE,
    CONFIG_KEY_PROFILE,
    CONFIG_KEY_VC_TYPES,
    Configuration,
)


class Command(BaseCommand):
    help = "The functional/simpliest way to create a superuser"

    def handle(self, *args, **options):
        for path in settings.LOCALE_PATHS:
            if not os.path.exists(path):
                os.mkdir(path)

        os.system("python manage.py migrate")

        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin",  # USERNAME
                "",  # MAIL. Set correct email or "". Incorrect email causes error in user/signals.py
                "admin",  # PASS
            )

        self._load_initial_data()

    def _load_initial_data(self):
        Configuration.objects.get_or_create(key=CONFIG_KEY_PROFILE, defaults={"value": "isbe"})
        Configuration.objects.get_or_create(key=CONFIG_KEY_APP, defaults={"value": "oid"})
        Configuration.objects.get_or_create(key=CONFIG_KEY_INSTANCE, defaults={"value": "isbe-instance"})
        Configuration.objects.get_or_create(key=CONFIG_KEY_API_VERSION, defaults={"value": "v1"})
        Configuration.objects.get_or_create(
            key=CONFIG_KEY_VC_TYPES, tag="representative", defaults={"value": "RepresentativeVC"}
        )
        Configuration.objects.get_or_create(key=CONFIG_KEY_VC_TYPES, tag="employee", defaults={"value": "EmployeeVC"})
