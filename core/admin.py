
from django.contrib import admin
from .models import Transaction, Nudge

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("posted_at","merchant_raw","category","amount_cents")
    list_filter  = ("category",)
    search_fields = ("merchant_raw","memo")

@admin.register(Nudge)
class NudgeAdmin(admin.ModelAdmin):
    list_display = ("type","status","created_at")
    list_filter  = ("status","type")
