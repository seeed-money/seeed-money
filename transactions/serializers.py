# transactions/serializers.py
from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source="account.account_name")

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_name",
            "transaction_type",
            "amount",
            "balance_after",  # 잔액
            "description",
            "transaction_method",  # 결제수단
            "transaction_at",
        ]
        read_only_fields = ["transaction_at", "balance_after", "user"]
