import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from issuance.views import CONFIG_KEY_PROFILE, CONFIG_KEY_VC_TYPES, Configuration


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
        if Configuration.objects.count() > 0:
            return  # Already initialized

        Configuration.objects.create(key=CONFIG_KEY_PROFILE, value="isbe")
        Configuration.objects.create(key=CONFIG_KEY_VC_TYPES, value="RepresentativeVC", tag="representative")
        Configuration.objects.create(key=CONFIG_KEY_VC_TYPES, value="EmployeeVC", tag="employee")
