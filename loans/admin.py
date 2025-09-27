from django.contrib import admin
from .models import Loan, Offer, Repayment, Profile
# Register your models here.

admin.site.register(Profile)
admin.site.register(Loan)
admin.site.register(Offer)
admin.site.register(Repayment)