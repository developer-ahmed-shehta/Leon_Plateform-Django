from datetime import timedelta, date
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Loan, Offer, Repayment, Profile
from .serializers import LoanSerializer, OfferSerializer, RepaymentSerializer, UserSerializer, RegisterSerializer
from decimal import Decimal
from django.db import transaction

# ------------------------------------
# User Management
# ------------------------------------

@api_view(["POST"])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ------------------------------------
# Borrower Actions
# ------------------------------------

# Borrower: Create Loan Request
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_loan_request(request):
    amount = request.data.get("amount")
    term_months = request.data.get("term_months", 6)
    loan = Loan.objects.create(borrower=request.user, amount=amount, term_months=term_months)
    return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


# Borrower: Accept Offer
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_offer(request, offer_id):
    try:
        offer = Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        return Response({"error": "Offer not found"}, status=404)

    loan = offer.loan
    lender_profile = offer.lender.profile

    if lender_profile.balance < offer.total_amount:
        return Response({"error": "Lender does not have enough balance"}, status=400)

    # Transaction to ensure atomicity of balance deduction and loan update
    with transaction.atomic():
        lender_profile.balance -= Decimal(str(offer.total_amount))
        lender_profile.save()

        loan.lender = offer.lender
        loan.interest_rate = offer.interest_rate
        loan.funded_at = timezone.now()
        loan.status = "FUNDED"
        loan.save()

    # Create repayment schedule
    installment = loan.total_payable / loan.term_months
    for i in range(loan.term_months):
        Repayment.objects.create(
            loan=loan,
            borrower=loan.borrower,
            amount=installment,
            due_date=date.today() + timedelta(days=30 * (i + 1))
        )

    return Response(LoanSerializer(loan).data)


# Borrower: Pay Installment
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pay_installment(request, repayment_id):
    try:
        repayment = Repayment.objects.get(id=repayment_id, borrower=request.user, paid=False)
    except Repayment.DoesNotExist:
        return Response({"error": "Repayment not found or already paid"}, status=404)

    repayment.paid = True
    repayment.paid_at = timezone.now()
    repayment.save()

    # Check if loan is completed
    loan = repayment.loan
    if not loan.repayments.filter(paid=False).exists():
        loan.status = "COMPLETED"
        loan.save()

    return Response(RepaymentSerializer(repayment).data)


# Borrower: My Loans
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_loans(request):
    loans = Loan.objects.filter(borrower=request.user)
    return Response(LoanSerializer(loans, many=True).data)


# Borrower: Repayments for Loan
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def loan_repayments(request, loan_id):
    repayments = Repayment.objects.filter(loan__id=loan_id, borrower=request.user)
    return Response(RepaymentSerializer(repayments, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def loan_offers(request, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id, borrower=request.user)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=404)

    offers = loan.offers.filter(loan=loan)
    return Response(OfferSerializer(offers, many=True).data)
# ------------------------------------
# Lender Actions
# ------------------------------------
# Lender: List open loans
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_open_loans(request):
    loans = Loan.objects.filter(status="OPEN", lender__isnull=True)
    return Response(LoanSerializer(loans, many=True).data)


# Lender: Create Offer
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_lender_offer(request, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id, status="OPEN", lender__isnull=True)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not available"}, status=404)

    interest_rate = request.data.get("interest_rate", 15.0)
    offer = Offer.objects.create(loan=loan, lender=request.user, interest_rate=interest_rate)
    return Response(OfferSerializer(offer).data, status=201)


# Lender: My Offers
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_offers(request):
    offers = Offer.objects.filter(lender=request.user)
    return Response(OfferSerializer(offers, many=True).data)

