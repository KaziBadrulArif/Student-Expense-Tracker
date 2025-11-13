
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Transaction(models.Model):
    """
    One row per purchase/charge.
    For MVP we skip auth and keep user nullable; you can hook it later.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # the date the transaction posted on your statement
    posted_at = models.DateField()

    # raw merchant text from CSV (e.g., "UBER *TRIP 9AK")
    merchant_raw = models.CharField(max_length=255)

    # a cleaner, normalized version derived from merchant_raw (e.g., "UBER *TRIP")
    merchant_norm = models.CharField(max_length=255, blank=True, default="")

    # loose bucket like "Groceries", "Subscription", etc.
    category = models.CharField(max_length=64, blank=True, default="")

    # store money as integer cents to avoid float math issues
    amount_cents = models.IntegerField()

    # nice-to-have metadata for future features/filters
    city = models.CharField(max_length=128, blank=True, default="")
    channel = models.CharField(max_length=32, blank=True, default="")  # "card", "e-transfer", etc.
    memo = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["posted_at", "category"]),
        ]

    def __str__(self):
        return f"{self.posted_at} {self.merchant_raw} ${self.amount_cents/100:.2f}"

class Nudge(models.Model):
    """
    A simple “suggestion” we surface based on the user’s spending patterns.
    """
    STATUS = [
        ("pending", "pending"),
        ("sent", "sent"),
        ("dismissed", "dismissed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # short machine name (e.g., "delivery_cap", "coffee_swap", "burn_rate")
    type = models.CharField(max_length=64)

    # human-readable copy that shows up in the UI
    message = models.TextField()

    # free-form JSON so we can store why this nudge happened
    triggered_by = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=16, choices=STATUS, default="pending")

    def __str__(self):
        return f"[{self.type}] {self.message[:40]}..."
