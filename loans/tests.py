from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Profile, Loan, Offer, Repayment
from django.urls import reverse

class LendingPlatformTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create borrower and lender
        self.register_user("borrower", "borrow@gmail.com", "pass123", "BORROWER")
        self.register_user("lender", "lender@gmail.com", "pass123", "LENDER")

        self.borrower = User.objects.get(username="borrower")
        self.lender = User.objects.get(username="lender")

        self.borrower_profile = Profile.objects.get(user=self.borrower)
        self.lender_profile = Profile.objects.get(user=self.lender)
        
    def register_user(self, username, email, password, role):
        return self.client.post(reverse("register"), {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        })


    def authenticate(self, username, password):
        """Login with JWT and set token for client."""
        response = self.client.post(reverse("token_obtain_pair"), {"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_borrower_creates_loan_request(self):
        self.authenticate("borrower", "pass123")
        response = self.client.post(reverse("create_loan_request"), {"amount": "5000", "term_months": 6})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)

        self.assertEqual(Loan.objects.first().borrower, self.borrower)

    def test_lender_creates_offer(self):
        # Borrower creates loan
        self.authenticate("borrower", "pass123")
        loan_response = self.client.post(reverse("create_loan_request"), {"amount": "5000", "term_months": 6})
        loan_id = loan_response.data["id"]

        # Lender creates offer
        self.authenticate("lender", "pass123")
        offer_response = self.client.post(reverse("create_lender_offer", args=[loan_id]),{"interest_rate": "12.5"})
        self.assertEqual(offer_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Offer.objects.first().lender, self.lender)

    def test_borrower_accepts_offer_and_repayments_created(self):

        lender_balance_before = self.lender_profile.balance # 10000
        borrower_balance_before = self.borrower_profile.balance # 0


        # ---------------------
        # first loan cycle
        # ---------------------

        # Borrower creates loan
        self.authenticate("borrower", "pass123")
        loan_response = self.client.post(reverse("create_loan_request"), {"amount": "5000", "term_months": 6})
        loan_id = loan_response.data["id"]

        # Lender creates offer
        self.authenticate("lender", "pass123")
        offer_response = self.client.post(reverse("create_lender_offer", args=[loan_id]), {"interest_rate": "10"})
        offer_id = offer_response.data["id"]

        # Borrower accepts offer
        self.authenticate("borrower", "pass123")
        accept_response = self.client.post(reverse("accept_offer", args=[offer_id]))
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)

        # Verify loan status and repayments
        loan = Loan.objects.get(id=loan_id)
        self.assertEqual(loan.status, "FUNDED")
        self.assertEqual(Repayment.objects.filter(loan=loan).count(), 6)
        self.assertEqual(float(loan.lender.profile.balance), float(lender_balance_before) - float(loan.amount) - float(loan.fee))
        print("Lender balance after first loan funded:", self.lender.profile.balance)

        # ---------------------
        # second second cycle
        # ---------------------

        # Borrower creates loan
        self.authenticate("borrower", "pass123")
        loan_response = self.client.post(reverse("create_loan_request"), {"amount": "6000", "term_months": 6})
        loan_id = loan_response.data["id"]

        # Lender creates offer
        print(f"lender balance before create offer {self.lender.profile.balance}")
        self.authenticate("lender", "pass123")
        offer_response = self.client.post(reverse("create_lender_offer", args=[loan_id]), {"interest_rate": "10"})
        offer_id = offer_response.data["id"]
        self.assertEqual(offer_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)

        # Borrower accepts offer
        print(f"offer id {offer_id}, offer total amount: {Offer.objects.get(id=offer_id).total_amount}, lender balance: {self.lender.profile.balance}")
        self.authenticate("borrower", "pass123")
        accept_response = self.client.post(reverse("accept_offer", args=[offer_id]))

        # Verify loan status and repayments
        loan = Loan.objects.get(id=loan_id)
        self.assertEqual(accept_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(loan.status, "OPEN")
        self.assertEqual(Repayment.objects.filter(loan=loan).count(), 0)
        self.assertEqual(loan.lender, None)



    def test_borrower_pays_installments_until_completed(self):
        self.authenticate("borrower", "pass123")
        loan = Loan.objects.create(borrower=self.borrower, amount=1000, term_months=2, status="FUNDED")
        Repayment.objects.create(loan=loan, borrower=self.borrower, amount=500, due_date="2025-10-01")
        Repayment.objects.create(loan=loan, borrower=self.borrower, amount=500, due_date="2025-11-01")

        for repayment in loan.repayments.all():
            response = self.client.post(reverse("pay_installment", args=[repayment.id]))
            self.assertEqual(response.status_code, 200)

        loan.refresh_from_db() # Refresh to get updated status
        self.assertEqual(loan.status, "COMPLETED")
