import csv, io
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import Transaction, Nudge
from .serializers import TransactionSerializer, NudgeSerializer
from .rules import normalize_and_categorize, build_insights, suggest_nudges

# --- helpers ---------------------------------------------------------

def _ordered(qs):
    """Stable ordering for predictable responses."""
    return qs.order_by("posted_at", "id")

def _filter_month(qs, month_param):
    """Filter a QuerySet by ?month=YYYY-MM (optional)."""
    if not month_param:
        return qs
    y, m = map(int, month_param.split("-"))
    return qs.filter(posted_at__year=y, posted_at__month=m)

# --- views -----------------------------------------------------------

@method_decorator(never_cache, name="dispatch")
class UploadCSVView(APIView):
    """
    POST /api/transactions/upload[?mode=replace&month=YYYY-MM]
    Body: form-data with key "file" -> CSV
    Headers: posted_at,merchant,amount,city,channel,memo
    """
    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"error": "file required"}, status=400)

        mode = request.GET.get("mode")      # e.g., "replace"
        month = request.GET.get("month")    # e.g., "2025-10" (used when mode=replace)

        raw = f.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(raw))

        with transaction.atomic():
            # optional: replace that month first
            if mode == "replace" and month:
                _filter_month(Transaction.objects.all(), month).delete()

            created = 0
            for row in reader:
                t = Transaction(
                    posted_at=row["posted_at"],
                    merchant_raw=(row.get("merchant","") or "").strip(),
                    amount_cents=int(round(float(row.get("amount","0")) * 100)),
                    city=row.get("city","") or "",
                    channel=row.get("channel","") or "",
                    memo=row.get("memo","") or "",
                )
                normalize_and_categorize(t)
                t.save()
                created += 1

        return Response({"ok": True, "created": created, "mode": mode, "month": month}, status=201)


@method_decorator(never_cache, name="dispatch")
class TransactionsView(APIView):
    """GET /api/transactions[?month=YYYY-MM] -> recent transactions."""
    def get(self, request):
        month = request.GET.get("month")
        qs = _ordered(_filter_month(Transaction.objects.all(), month))[:500]
        return Response(TransactionSerializer(qs, many=True).data)


@method_decorator(never_cache, name="dispatch")
class InsightsView(APIView):
    """GET /api/insights[?month=YYYY-MM] -> totals, by_category, top_merchants, forecast."""
    def get(self, request):
        month = request.GET.get("month")
        qs = list(_ordered(_filter_month(Transaction.objects.all(), month)))
        return Response(build_insights(qs))


@method_decorator(never_cache, name="dispatch")
class NudgesView(APIView):
    """
    GET /api/nudges -> list
    POST /api/nudges -> create manual nudge (rare in MVP)
    """
    def get(self, request):
        qs = Nudge.objects.order_by("-created_at")[:100]
        return Response(NudgeSerializer(qs, many=True).data)

    def post(self, request):
        ser = NudgeSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


@method_decorator(never_cache, name="dispatch")
class SuggestNudgesView(APIView):
    """
    POST /api/nudges/suggest[?month=YYYY-MM]
    Re-run rules for the chosen month and upsert (avoid duplicates by type).
    """
    def post(self, request):
        month = request.GET.get("month")
        txns = list(_ordered(_filter_month(Transaction.objects.all(), month)))
        suggestions = suggest_nudges(txns)

        out = []
        for s in suggestions:
            n, _ = Nudge.objects.update_or_create(
                type=s["type"], status="pending",
                defaults={"message": s["message"], "triggered_by": s.get("triggered_by", {})}
            )
            out.append(n)

        return Response(NudgeSerializer(out, many=True).data, status=201)



@method_decorator(never_cache, name="dispatch")
class DevResetView(APIView):
    """POST /api/dev/reset -> wipe transactions + nudges (DEBUG only; wire in urls if you want)."""
    def post(self, request):
        Transaction.objects.all().delete()
        Nudge.objects.all().delete()
        return Response({"ok": True, "cleared": True})