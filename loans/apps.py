# loans/apps.py
from django.apps import AppConfig

class LoansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loans'

    def ready(self):
        # Import here to avoid AppRegistryNotReady errors
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json

        # Run this only if the task does not exist
        if not PeriodicTask.objects.filter(name="check_due_repayments").exists():
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute="0",
                hour="*",
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
            )

            PeriodicTask.objects.create(
                name="check_due_repayments",
                task="loans.tasks.check_due_repayments",
                crontab=schedule,
                enabled=True,
                kwargs=json.dumps({}),
            )
            print("Periodic task 'check_due_repayments' created.")