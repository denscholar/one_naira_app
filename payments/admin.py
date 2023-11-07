from django.contrib import admin
from .models import Transaction, TransactionCharges, TransactionFee, Wallet, Deposit, Payment


class TransactionFeeAdmin(admin.ModelAdmin):
    list_display = ("id", "fee")
    fields = ("fee",)


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "payer",
        "description",
        "amount",
        "transaction_ref",
        "transaction_type",
        "status",
        "timestamp",
    )

    search_fields = (
        "payer__user__first_name",
        "payer__user__last_name",
        "payee__user__first_name",
        "payee__user__last_name",
    )
    readonly_fields = ("timestamp",)


class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "wallet_identifier",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__first_name", "user__last_name", "wallet_identifier")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Deposit)
class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "transaction_type", "amount", "timestamp", "status")
    list_display_links = ("wallet",)
    readonly_fields = ("timestamp",)


@admin.register(TransactionCharges)
class TransactionChargesAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction', 'charge_amount', 'created_at', )
    list_display_links = ("user",)
    readonly_fields = list_display


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payee_wallet_address', 'description', )
    list_display_links = ("user",)
    readonly_fields = list_display


admin.site.register(TransactionFee, TransactionFeeAdmin)
admin.site.register(Wallet, WalletAdmin)

admin.site.register(Transaction, TransactionAdmin)

