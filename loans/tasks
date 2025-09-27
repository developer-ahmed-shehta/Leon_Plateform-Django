from celery import shared_task
from django.utils import timezone
from .models import Repayment, Loan
from decimal import Decimal

@shared_task
def check_due_repayments():
    """
    Task that runs every hour to check overdue repayments
    and optionally notify borrowers.
    """
    now = timezone.now()
    due_repayments = Repayment.objects.filter(paid=False, due_date__lte=now)

    for repayment in due_repayments:
        # Example: update status or send notification
        loan = repayment.loan
        print(f"Repayment due for Loan {loan.id}, Borrower: {loan.borrower.username}, Amount: {repayment.amount}")

        # Optional: You could mark overdue flag
        repayment.overdue = True
        repayment.save()