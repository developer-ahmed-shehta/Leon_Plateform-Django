from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

class Profile(models.Model):
    ROLE_CHOICES = [
        ("BORROWER", "Borrower"),
        ("LENDER", "Lender"),
    ]
    """Extension of User to hold balance (for lender/borrower wallets)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # Additional fields
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default="BORROWER")

    def __str__(self):
        return f"{self.user.username} Profile"


class Loan(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("FUNDED", "Funded"),
        ("COMPLETED", "Completed"),
    ]

    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowed_loans")
    lender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="funded_loans", null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    term_months = models.PositiveIntegerField(default=6)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=3.75)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    funded_at = models.DateTimeField(null=True, blank=True)

    @property
    def total_payable(self):
        interest = (Decimal(self.amount) * (Decimal(self.interest_rate) / Decimal("100"))) * (Decimal(self.term_months) / Decimal("12"))
        return float(self.amount) + float(interest) + float(self.fee)

    def __str__(self):
        return f"Loan {self.id} - {self.borrower.username}"



@receiver(post_save, sender=Loan)
def clear_open_loans_cache(sender, instance, **kwargs):
    # Clear cache if a loan is created or status changes
    if instance.status == "OPEN" or instance.lender is None:
        cache.delete(settings.OPEN_LOANS_CACHE_KEY)


class Offer(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="offers")
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=3.75)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return float(self.loan.amount) + float(self.fee)

    def __str__(self):
        return f"Offer {self.id} on Loan {self.loan.id}"


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    overdue = models.BooleanField(default=False)

    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Repayment {self.id} - Loan {self.loan.id} - {self.amount}"
