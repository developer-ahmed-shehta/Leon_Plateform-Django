# loans/management/commands/setup_periodic_tasks.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

class Command(BaseCommand):
    help = "Setup periodic tasks for the lending platform"

    def handle(self, *args, **options):
        # Create crontab schedule: every hour at minute 0
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="*",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # Create or update the periodic task
        task, created = PeriodicTask.objects.update_or_create(
            name="check_due_repayments",
            defaults={
                "task": "loans.tasks.check_due_repayments",
                "crontab": schedule,
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Periodic task created successfully!"))
        else:
            self.stdout.write(self.style.SUCCESS("Periodic task updated successfully!"))
