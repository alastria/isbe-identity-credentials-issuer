import logging
import sys

from django.apps import AppConfig

logger = logging.getLogger("django")


class TasksConfig(AppConfig):
    name = "tasks"

    def ready(self, *args, **kwargs):
        from tasks.launch_tasks import LaunchScheduler

        is_manage_py = any(arg.casefold().endswith("manage.py") for arg in sys.argv)
        is_runserver = any(arg.casefold() == "runserver" for arg in sys.argv)

        if is_manage_py and is_runserver:
            # only run when runserver command is present
            logger.info(" ====>> TaskConfig <<===")
            LaunchScheduler.start()
