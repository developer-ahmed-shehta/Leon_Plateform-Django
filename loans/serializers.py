from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Loan, Offer, Repayment, Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )
        starting_balance = 10000 if role == "LENDER" else 0   # Initial balance for lenders to facilitate testing
        Profile.objects.create(user=user, role=role, balance=starting_balance)
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    balance = serializers.DecimalField(source="profile.balance", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "balance"]



class LoanSerializer(serializers.ModelSerializer):
    borrower = UserSerializer(read_only=True)
    lender = UserSerializer(read_only=True)
    total_payable = serializers.FloatField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id", "borrower", "lender", "amount", "term_months",
            "interest_rate", "fee", "status", "created_at", "funded_at",
            "total_payable"
        ]


class OfferSerializer(serializers.ModelSerializer):
    lender = UserSerializer(read_only=True)
    total_amount = serializers.FloatField(read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "loan", "lender", "interest_rate", "fee", "total_amount", "created_at"]


class RepaymentSerializer(serializers.ModelSerializer):
    borrower = UserSerializer(read_only=True)

    class Meta:
        model = Repayment
        fields = ["id", "loan", "borrower", "amount", "due_date", "paid", "paid_at"]
