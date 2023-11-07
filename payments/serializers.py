from rest_framework import serializers
from accounts.models import CustomUser
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from accounts.utils import send_otp
from .models import (
    Deposit,
    Payment,
    QrBarCode,
    Transaction,
    TransactionCharges,
    Wallet,
    TransactionFee,
)
from django.contrib.auth.hashers import check_password
from rest_framework import serializers

# from django.db import transaction
from django.conf import settings
import requests


def is_amount(value):
    if value <= 0:
        raise serializers.ValidationError(
            "Invalid amount. Input amount greater than zero"
        )
    return value


class Depositserializer(serializers.ModelSerializer):
    amount = serializers.FloatField(validators=[is_amount])

    class Meta:
        model = Deposit
        fields = ("amount",)


class TransactionChangePinSerializer(serializers.Serializer):
    old_transaction_pin = serializers.CharField(max_length=4)
    new_transaction_pin = serializers.CharField(max_length=4)

    def validate(self, data):
        if data["old_transaction_pin"] == data["new_transaction_pin"]:
            raise serializers.ValidationError(
                "You cannot use your old pin, please set a new pin"
            )
        return data

    def update(self, instance, validated_data):
        # Validate the old pin
        old_transaction_pin = validated_data.pop("old_transaction_pin")
        if not check_password(old_transaction_pin, instance.transaction_pin):
            raise serializers.ValidationError("Old transaction pin is incorrect")

        # Update the transaction pin with the new pin
        new_transaction_pin = validated_data.pop("new_transaction_pin")
        instance.transaction_pin = make_password(new_transaction_pin)
        instance.save()

        return instance


class QRCodeSerializer(serializers.ModelSerializer):
    wallet_id = serializers.ReadOnlyField(source="user.phone_number")

    class Meta:
        model = QrBarCode
        fields = ("id", "wallet_id")


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(validators=[is_amount])
    payee_wallet_address = serializers.CharField(required=True)
    description = serializers.CharField(max_length=50)

    class Meta:
        model = Payment
        fields = (
            "amount",
            "payee_wallet_address",
            "description",
        )

    def validate_payee_wallet_address(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Invalid payee wallet address.")
        if not value:
            raise serializers.ValidationError("Payee wallet address is required.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user  # Get the authenticated user
        amount = validated_data["amount"]
        payee_wallet_address = validated_data["payee_wallet_address"]
        description = validated_data["description"]

        # Retrieve the payer and payee wallets
        payer_wallet = user.wallet
        payee_wallet = Wallet.objects.get(wallet_identifier=payee_wallet_address)

        # retrieve the transaction fee
        transaction_fee = TransactionFee.objects.first().fee * amount

        if payer_wallet.wallet_identifier == payee_wallet.wallet_identifier:
            raise serializers.ValidationError(
                "Payer and payee cannot have the same wallet details."
            )

        if payer_wallet.balance < (amount + transaction_fee):
            raise serializers.ValidationError("Insufficient balance.")

        # Perform the payment transaction within a database transaction
        with transaction.atomic():
            # Update the payee wallet balance
            payee_wallet.balance += Decimal(amount)
            payee_wallet.save()

            # Debit the payer wallet balance
            payer_wallet.balance -= Decimal(amount)
            payer_wallet.save()

            # Create the Payment object
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                payee_wallet_address=payee_wallet_address,
                description=description,
            )

            # Create the Transaction object
            transaction = Transaction.objects.create(
                payer=payer_wallet,
                payee=payee_wallet,
                amount=amount,
                description=description,
                transaction_type="PAYMENT",
                status="COMPLETED",
            )

        return payment


class TransactionSerializer(serializers.ModelSerializer):
    deposit = Depositserializer(many=True, read_only=True)
    payment = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        exclude = ["payer", "payee"]
        read_only_fields = (
            "payee",
            "deposit",
            "payment",
            "transaction_ref",
            "status",
            "transaction_type",
            "timestamp",
        )

class WalletSerializer(serializers.ModelSerializer):
    debit = TransactionSerializer(many=True, read_only=True)
    credit = TransactionSerializer(many=True, read_only=True)
    deposit = Depositserializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ("user", "balance", "wallet_identifier", "debit", "credit", "funding")
        read_only_fields = fields
