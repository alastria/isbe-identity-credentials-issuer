# runapscheduler.py
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from issuance.enum import IssuedCredentialStatus
from issuance.models import IssuedCredential

logger = logging.getLogger("django")


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


JOB_NAME = "delete_credentials_expired_job"


def job_print(str):
    logger.info(f"{JOB_NAME}: {str}")


def delete_pending_expired_credentials_job():
    job_print("Running delete pending and expired credentials job...")

    now = timezone.now()
    count = 0
    expired_credentials = IssuedCredential.objects.filter(status=IssuedCredentialStatus.PENDING.value)
    for cred in expired_credentials:
        if cred.preauth_code_expires_in and cred.preauth_code_expires_in < now:
            count += 1
            job_print(f"Deleting credential: {cred.id}")
            cred.delete()
    job_print(f"Deleted {count} pending and expired credentials.")
    job_print("Delete credentials expired job completed.")


class LaunchScheduler:
    help = "Runs APScheduler."
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler_start = False

    def start():
        if LaunchScheduler.scheduler_start:
            return
        LaunchScheduler.scheduler_start = True

        if not LaunchScheduler.scheduler.get_job("delete_old_job_executions"):
            LaunchScheduler.scheduler.add_job(
                delete_old_job_executions,
                # Midnight on Monday, before start of the next work week.
                # trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
                trigger=CronTrigger(minute="00"),  # every hour
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added every hour job: 'delete_old_job_executions'.")

        if not LaunchScheduler.scheduler.get_job(JOB_NAME):
            LaunchScheduler.scheduler.add_job(
                delete_pending_expired_credentials_job,
                trigger=CronTrigger(minute="*", hour="*", day="*", month="*", day_of_week="*"),  # every hour
                id=JOB_NAME,  # The `id` assigned to each job MUST be unique
                replace_existing=True,
            )
            logger.info(f"Added job '{JOB_NAME}'.")

        # arrancar Launcher
        try:
            logger.info("Starting scheduler...")
            LaunchScheduler.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            LaunchScheduler.scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
