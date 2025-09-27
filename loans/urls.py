from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # User management
    path("register/", views.register_user, name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.my_profile, name="my_profile"),

    # Borrower actions
    path("v1/loan-requests/create/", views.create_loan_request, name="create_loan_request"),
    path("v1/offers/<int:offer_id>/accept/", views.accept_offer, name="accept_offer"),
    path("v1/repayments/<int:repayment_id>/pay/", views.pay_installment, name="pay_installment"),
    path("v1/my/loans/", views.my_loans, name="my_loans"),
    path("v1/loan/<int:loan_id>/repayments/", views.loan_repayments, name="loan_repayments"),
    path("v1/loans/<int:loan_id>/offers/", views.loan_offers, name="loan_offers"),

    # Lender actions
    path("v1/loans/current_loan/", views.list_open_loans, name="list_open_loans"),
    path("v1/loans/<int:loan_id>/offer/", views.create_lender_offer, name="create_lender_offer"),
    path("v1/my/offers/", views.my_offers, name="my_offers"),
]
