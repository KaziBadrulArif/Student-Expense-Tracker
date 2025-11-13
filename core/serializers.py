# core/serializers.py
# DRF serializers turn model instances into clean JSON and validate input.

from rest_framework import serializers
from .models import Transaction, Nudge

class TransactionSerializer(serializers.ModelSerializer):
    """Minimal, explicit fields for the API response."""
    class Meta:
        model = Transaction
        fields = [
            "id",
            "posted_at",
            "merchant_raw",
            "merchant_norm",
            "category",
            "amount_cents",
            "city",
            "channel",
            "memo",
        ]

class NudgeSerializer(serializers.ModelSerializer):
    """Surface the helpful text + metadata for the UI."""
    class Meta:
        model = Nudge
        fields = ["id", "created_at", "type", "message", "triggered_by", "status"]
