# core/rules.py
# A tiny, extensible, human-readable engine for categorization, insights, and smart nudges.

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Callable, Tuple
from dateutil.relativedelta import relativedelta

# === CONFIGURATION ===
# Easy to tweak — move to DB or user settings later
THRESHOLDS = {
    "delivery_cap": 6000,      # $60
    "coffee_swap": 2000,       # $20
    "subs_audit": 3000,        # $30
    "burn_rate_budget": 120000 # $1,200
}

# Category keyword mapping: (keyword, category)
CATEGORY_MAP = [
    ("UBEREATS", "Food Delivery"),
    ("UBER *TRIP", "Transport"),
    ("STARBUCKS", "Coffee"),
    ("SAFEWAY", "Groceries"),
    ("WALMART", "Household"),
    ("SHELL", "Gas"),
    ("NETFLIX", "Subscription"),
    ("SPOTIFY", "Subscription"),
    ("AMAZON DIGITAL", "Subscription"),
    ("AMAZON", "Retail"),
    ("TELUS", "Utilities"),
    ("RENT", "Rent"),
    ("RESTAURANT", "Dining"),
]

# === HELPERS ===
def _cents_to_dollars(cents: int) -> Decimal:
    return Decimal(cents) / 100

def _month_end(d: date) -> date:
    """Return last day of the month for given date."""
    next_month = d.replace(day=1) + relativedelta(months=1)
    return next_month - relativedelta(days=1)

def _days_in_month(d: date) -> int:
    return _month_end(d).day

def _safe_div(a: int, b: int) -> int:
    return a // b if b else 0

# === CORE LOGIC ===
def normalize_and_categorize(txn) -> None:
    """
    Mutate transaction in-place:
    - merchant_norm: cleaned merchant name
    - category: inferred spending category
    """
    raw = (txn.merchant_raw or "").upper().strip()
    for key, cat in CATEGORY_MAP:
        if key in raw:
            txn.merchant_norm = key.title()
            txn.category = cat
            return
    # Fallback
    txn.merchant_norm = raw.title() if raw else "Unknown"
    txn.category = "Other"


def build_insights(transactions: List[Any]) -> Dict[str, Any]:
    """
    Compute spending insights:
    - Total, by category, top merchants
    - Daily average + accurate monthly forecast
    - % share per category
    """
    if not transactions:
        return {
            "total_cents": 0,
            "by_category": {},
            "by_category_pct": {},
            "top_merchants": [],
            "daily_avg_cents": 0,
            "month_forecast_cents": 0,
            "days_observed": 0,
            "month_days": 0,
        }

    total_cents = 0
    by_cat: Dict[str, int] = defaultdict(int)
    by_merchant: Dict[str, int] = defaultdict(int)
    days_seen = set()
    month_hint = None

    for t in transactions:
        amount = getattr(t, "amount_cents", 0)
        total_cents += amount
        cat = getattr(t, "category", "Other")
        merchant = getattr(t, "merchant_norm", None) or getattr(t, "merchant_raw", "Unknown")
        posted = getattr(t, "posted_at", None)
        
        by_cat[cat] += amount
        by_merchant[merchant] += amount
        if posted:
            days_seen.add(posted)
            month_hint = month_hint or posted

    days_observed = max(1, len(days_seen))
    daily_avg_cents = _safe_div(total_cents, days_observed)

    # Accurate forecast: use actual month length
    month_days = _days_in_month(month_hint) if month_hint else 30
    forecast_cents = daily_avg_cents * month_days

    # % of total
    total_dec = Decimal(total_cents)
    by_cat_pct = {
        cat: float((Decimal(cents) / total_dec) * 100) if total_dec else 0.0
        for cat, cents in by_cat.items()
    }

    top_merchants = sorted(
        by_merchant.items(),
        key=lambda kv: kv[1],
        reverse=True
    )[:5]

    return {
        "total_cents": total_cents,
        "by_category": dict(by_cat),
        "by_category_pct": by_cat_pct,
        "top_merchants": top_merchants,
        "daily_avg_cents": daily_avg_cents,
        "month_forecast_cents": forecast_cents,
        "days_observed": days_observed,
        "month_days": month_days,
    }


# === NUDGE ENGINE (Extensible Rule Functions) ===
NudgeRule = Callable[[List[Any], Dict[str, Any]], List[Dict[str, Any]]]

def _nudge_delivery_cap(txns: List[Any], insights: Dict[str, Any]) -> List[Dict]:
    delivery_cents = insights["by_category"].get("Food Delivery", 0)
    if delivery_cents > THRESHOLDS["delivery_cap"]:
        return [{
            "type": "delivery_cap",
            "message": f"Food delivery at ${_cents_to_dollars(delivery_cents):.2f}. "
                       f"Try a ${_cents_to_dollars(THRESHOLDS['delivery_cap']):.0f}/week cap + one home-cooked meal.",
            "triggered_by": {"delivery_cents": delivery_cents},
            "suggestion": "Batch prep on Sunday → save $40–80/mo"
        }]
    return []


def _nudge_coffee_swap(txns: List[Any], insights: Dict[str, Any]) -> List[Dict]:
    coffee_cents = insights["by_category"].get("Coffee", 0)
    if coffee_cents > THRESHOLDS["coffee_swap"]:
        saved = _cents_to_dollars(coffee_cents - THRESHOLDS["coffee_swap"])
        return [{
            "type": "coffee_swap",
            "message": f"Coffee spend: ${_cents_to_dollars(coffee_cents):.2f}. "
                       f"Swap 3 café trips for home brew → save ~${saved * 4:.0f}/mo.",
            "triggered_by": {"coffee_cents": coffee_cents},
            "suggestion": "Invest in a $15 reusable cup or French press"
        }]
    return []


def _nudge_subs_audit(txns: List[Any], insights: Dict[str, Any]) -> List[Dict]:
    subs_cents = insights["by_category"].get("Subscription", 0)
    if subs_cents > THRESHOLDS["subs_audit"]:
        # Find top 3 subscriptions by merchant
        subs_merchants = {
            m: c for m, c in insights.get("by_merchant", {}).items()
            if any(sub in m.upper() for sub in ["NETFLIX", "SPOTIFY", "AMAZON DIGITAL", "APPLE", "YOUTUBE"])
        }
        top_subs = sorted(subs_merchants.items(), key=lambda x: x[1], reverse=True)[:3]
        names = [name.split()[0] for name, _ in top_subs] if top_subs else ["..."]

        return [{
            "type": "subs_audit",
            "message": f"Subscriptions: ${_cents_to_dollars(subs_cents):.2f}/mo "
                       f"({', '.join(names)}...). Schedule a 10-min audit.",
            "triggered_by": {"subs_cents": subs_cents, "top_subs": top_subs},
            "suggestion": "Cancel one unused sub → instant savings"
        }]
    return []


def _nudge_burn_rate(txns: List[Any], insights: Dict[str, Any]) -> List[Dict]:
    forecast = insights["month_forecast_cents"]
    budget = THRESHOLDS["burn_rate_budget"]
    if forecast > budget:
        over = _cents_to_dollars(forecast - budget)
        return [{
            "type": "burn_rate",
            "message": f"On pace for ${_cents_to_dollars(forecast):.0f} vs ${_cents_to_dollars(budget):.0f} budget "
                       f"(+${over:.0f}). Try a 7-day '10% freeze'.",
            "triggered_by": {"forecast_cents": forecast, "budget_cents": budget},
            "suggestion": "Pause non-essentials: dining, shopping, subs"
        }]
    return []


# Register all nudge rules
NUDGE_RULES: List[NudgeRule] = [
    _nudge_delivery_cap,
    _nudge_coffee_swap,
    _nudge_subs_audit,
    _nudge_burn_rate,
]


def suggest_nudges(transactions: List[Any]) -> List[Dict[str, Any]]:
    """
    Run all registered nudge rules. Returns prioritized, actionable suggestions.
    """
    if not transactions:
        return []

    insights = build_insights(transactions)
    nudges: List[Dict[str, Any]] = []

    for rule in NUDGE_RULES:
        try:
            nudges.extend(rule(transactions, insights))
        except Exception as e:
            # Never break on one bad rule
            continue

    # Optional: dedupe or prioritize
    return nudges[:5]  # limit to top 5