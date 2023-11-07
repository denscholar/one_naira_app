from decimal import Decimal
import random
from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.hashers import is_password_usable
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from accounts.models import CustomUser
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
import uuid


class TransactionFee(models.Model):
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction Fee: {self.fee}"

    def return_current_fee(self):
        return self.fee


class TransactionCharges(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="charges"
    )
    transaction = models.ForeignKey(
        "Transaction", on_delete=models.CASCADE, related_name="transactions"
    )
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Charge for Transaction: {self.transaction}"


class Wallet(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=50, default="NGN")
    wallet_identifier = models.CharField(max_length=10, unique=True, primary_key=True)
    # transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, related_name="transaction")
    # payment = models.ForeignKey("Payment", on_delete=models.CASCADE, related_name="payment")
    # deposit = models.ForeignKey("Deposit", on_delete=models.CASCADE, related_name="deposit")
    # withdrawal = models.ForeignKey("Withdrawal", on_delete=models.CASCADE, related_name="withdrawal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set wallet_address to user's phone number if not already set
        if not self.wallet_identifier:
            phone_number = self.user.phone_number
            self.wallet_identifier = phone_number[-10:]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Wallet"


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ("PAYMENT", "Payment"),
        ("TRANSFER", "Transfer"),
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
    )
    TRANSACTION_STATUS = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    )
    payer = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="debit", blank=True, null=True
    )
    payee = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="credit", blank=True, null=True
    )
    transaction_ref = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True,
    )
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    transaction_type = models.CharField(
        max_length=200, null=True, choices=TRANSACTION_TYPE
    )
    status = models.CharField(max_length=200, null=True, choices=TRANSACTION_STATUS)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.payer}"

    def save(self, *args, **kwargs):
        if not self.transaction_ref:
            while True:
                try:
                    random_suffix = str(
                        random.randint(1000, 9999)
                    )  # Generate a random 4-digit number
                    self.transaction_ref = f"{uuid.uuid4().hex[:28]}-{random_suffix}"
                    break
                except IntegrityError:
                    pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transactions for {self.payer.user.first_name + ' ' + self.payer.user.last_name}"


class Deposit(models.Model):
    TRANSACTION_STATUS = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    )
    wallet = models.ForeignKey(
        Wallet, null=True, on_delete=models.CASCADE, related_name="funding"
    )
    transaction_type = models.CharField(
        max_length=200,
        null=True,
        default="Deposit",
    )
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=100,
        null=True,
        choices=TRANSACTION_STATUS,
    )

    def __str__(self):
        return "Fund wallet"

    @transaction.atomic
    def save(self, *args, **kwargs):
        wallet_balance = self.wallet.balance
        amount = Decimal(str(self.amount))
        wallet_balance += amount
        self.wallet.balance = wallet_balance
        self.status = "Completed"
        self.wallet.save()
        super().save(*args, **kwargs)


class Payment(models.Model):
    TRANSACTION_STATUS = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="debit")
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    payee_wallet_address = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=50)
    status = models.CharField(max_length=100, null=True, choices=TRANSACTION_STATUS)
    timestamp = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return f"{self.user.phone_number} paid {self.amount} to {self.payee_wallet_address}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.status = "Completed"
        super().save(*args, **kwargs)


class Transfer(models.Model):
    pass


class QrBarCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='qr_code')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created = models.TimeField(auto_now_add=True)

    
