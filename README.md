# Spend Insights + Nudges

Upload your bank CSV → see where money goes → get simple, actionable nudges.  
Built for students (and busy humans) who want clarity without spreadsheets.

---

## ✨ Features

- **CSV import** (drag & drop) — headers: `posted_at,merchant,amount,city,channel,memo`
- **Auto-categorization** (keywords → Groceries, Delivery, Coffee, etc.)
- **Insights**: totals, category split, top merchants, forecast
- **Nudges**: delivery cap, subscription audit, burn-rate (idempotent; no duplicates)
- **“Replace month” uploads** — re-import same month without double-counting
- **Simple budgets** (Groceries / Delivery / Coffee / Household) with progress bars
- **Dev reset** endpoint (optional) for quick demos

---

## 🧱 Tech Stack

- **Backend:** Django 5 + Django REST Framework, `django-cors-headers`
- **Frontend:** React (Vite)
- **DB:** SQLite (local) or Postgres (via Docker)
- **Extras:** `python-dateutil` for date math

---

## 📁 Project Structure

```
Student-Expense-Tracker/
├─ server/                  # Django (optional: your root may already be config/ + core/)
│  ├─ config/               # settings, urls
│  ├─ core/                 # models, views, serializers, rules
│  ├─ requirements.txt
│  └─ Dockerfile
├─ client/                  # React (Vite)
│  ├─ src/
│  ├─ index.html
│  └─ vite.config.js
├─ data/                    # (optional) sample CSVs (gitignored by default)
├─ docker-compose.yml
├─ .gitignore
└─ README.md
```

> If you started without `server/` and placed Django at repo root, adjust paths accordingly.

---

## 🚀 Quick Start

### 1) Backend (Local, SQLite)

```bash
# Windows PowerShell
python -m venv .venv
. .\\.venv\\Scripts\\Activate.ps1
pip install -r server/requirements.txt  # or install Django, DRF, cors-headers, dateutil
python manage.py migrate
python manage.py runserver
```

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
python manage.py migrate
python manage.py runserver
```

Django API: http://127.0.0.1:8000

Make sure `config/settings.py` has:
```python
INSTALLED_APPS += ["rest_framework", "corsheaders", "core"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", *MIDDLEWARE]
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173"]
```

### 2) Frontend (Vite)

```bash
cd client
npm install
npm run dev
```

React app: http://127.0.0.1:5173

---

## 🐳 Run with Docker (Postgres)

Prereqs: Docker Desktop.

**docker-compose.yml** runs:
- `db` (Postgres 15)
- `api` (Django, exposes 8000)
- optional `frontend` (Node dev server on 5173)

```bash
docker compose up --build
```

Django: http://127.0.0.1:8000  
React:  http://127.0.0.1:5173

**Django settings for Postgres (env-driven):**
```python
import os
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DB_NAME", "spend"),
    "USER": os.getenv("DB_USER", "spend"),
    "PASSWORD": os.getenv("DB_PASSWORD", "spend"),
    "HOST": os.getenv("DB_HOST", "localhost"),
    "PORT": os.getenv("DB_PORT", "5432"),
  }
}
CORS_ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5173").split(",")
```

**Handy Docker commands**
```bash
docker compose logs -f api
docker compose exec api python manage.py migrate
docker compose exec api bash
docker compose down           # stop
docker compose down -v        # stop + wipe volumes (DB reset)
```

---

## 📤 CSV Format

The API expects UTF-8 CSV with headers:

```
posted_at,merchant,amount,city,channel,memo
2025-10-02,SAFEWAY #304,42.17,Calgary,card,groceries
2025-10-02,STARBUCKS 1234,5.45,Calgary,card,coffee
2025-10-03,UBER *TRIP 9AK,17.20,Calgary,card,ride home
```

- `posted_at` = `YYYY-MM-DD`
- `amount` = number only (e.g., `17.20`, not `$17.20`)

---

## 🔌 API Endpoints (MVP)

| Method | Path                              | Notes |
|-------:|-----------------------------------|------|
| POST   | `/api/transactions/upload`        | Body: form-data `file=@file.csv` |
| GET    | `/api/transactions`               | Optional `?month=YYYY-MM` |
| GET    | `/api/insights`                   | Optional `?month=YYYY-MM` |
| POST   | `/api/nudges/suggest`             | Optional `?month=YYYY-MM` |
| GET    | `/api/nudges`                     | List nudges |
| POST   | `/api/dev/reset` (optional)       | Dev-only reset (DEBUG) |

**Idempotent upload (no double counts)**  
Use query params on upload:

- `mode=replace` — delete that month’s rows first
- `month=YYYY-MM` — month to target

**Examples**
```bash
# Replace October 2025 and import afresh
curl -X POST \
  -F "file=@data/sample_transactions.csv;type=text/csv" \
  "http://127.0.0.1:8000/api/transactions/upload?mode=replace&month=2025-10"

# Insights + Nudges
curl "http://127.0.0.1:8000/api/insights?month=2025-10"
curl -X POST "http://127.0.0.1:8000/api/nudges/suggest?month=2025-10"
```

---

## 🧠 How nudges work (rules)

- **delivery_cap** — if “Food Delivery” spend crosses threshold (~$60 in sample)
- **subs_audit** — if Subscription total crosses threshold (e.g., > $30)
- **burn_rate** — naive forecast vs a monthly budget (improve by ignoring fixed bills)

All nudges are **upserts** by `type` → hitting “Re-run suggestions” won’t create duplicates.

---

## 🖥 Frontend UX (what to expect)

- Sticky topbar + big **Upload Transactions** dropzone/button
- After upload, you’ll see:
  - Insight cards (Total, Daily Avg, Month Forecast, Top Merchants, Categories)
  - Budgets (Groceries / Delivery / Coffee / Household) with progress bars
  - Nudges list + “Re-run suggestions” button

> If the page is blank, check browser **Console**. Common fixes are in **Troubleshooting** below.

---

## 🧪 Dev Tips

**Flush data (local):**
```bash
python manage.py flush --no-input
```

**Selective delete (Django shell):**
```bash
python manage.py shell
>>> from core.models import Transaction, Nudge
>>> Transaction.objects.all().delete()
>>> Nudge.objects.all().delete()
>>> exit()
```

**Never-cache responses (dev)**  
Views are decorated with `@never_cache` in `core/views.py` so you always fetch fresh data.

---

## 🐛 Troubleshooting

- **White screen in React**
  - Install plugin & config:
    ```bash
    cd client && npm i -D @vitejs/plugin-react
    ```
    `vite.config.js`
    ```js
    import react from '@vitejs/plugin-react';
    export default { plugins: [react()], server: { port: 5173 } };
    ```
  - Check Console for the first error, fix line shown.

- **CORS error**
  - Add frontend origin to `CORS_ALLOWED_ORIGINS` in Django and restart `runserver`.

- **Re-uploading the same CSV doubles totals**
  - Use `?mode=replace&month=YYYY-MM` on upload.
  - (Optional) Add file-hash gating (`ImportBatch`) to skip exact duplicates.

- **API can’t start / missing attributes**
  - Ensure `core/views.py` defines: `UploadCSVView`, `TransactionsView`, `InsightsView`, `NudgesView`, `SuggestNudgesView`.
  - Ensure `core/serializers.py` and `core/rules.py` exist with the right names.

---

## 🗺️ Roadmap

- Budget persistence (model + `/api/budgets`)
- Variable-only forecast (ignore fixed categories like Rent/Utilities)
- Charts (category pie, trend line)
- Auth (per-user data)
- Statement parsers for bank-specific exports

---



## 🤝 Contributing

PRs welcome! Please keep commits small and include a quick before/after note for any UI change.

---



### Credits

Built by humans who hate spreadsheets and love simple guardrails. If this helps you, ⭐ the repo!
