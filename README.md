# Optionality Tracker

Income-focused tracker with FastAPI + SQLite backend and React + TypeScript frontend.

## Pre-implementation notes

### 1) Brief plan (files)
1. Backend model/settings and deterministic readiness computation (`backend/app/models.py`, `backend/app/income_model.py`, `backend/app/schemas.py`, `backend/app/main.py`, `backend/app/analytics.py`).
2. Frontend dashboard + income model editor UI (`frontend/src/pages/DashboardPage.tsx`, `frontend/src/pages/IncomeModelPage.tsx`, `frontend/src/api.ts`, `frontend/src/types.ts`, `frontend/src/App.tsx`).
3. Tests + docs (`backend/tests/test_income_model.py`, `README.md`).

### 2) Income Target Model definition
Variables:
- Capitals in `[0..1]`: Skill `S`, Network `N`, Lead `L`, Energy stability `E`.
- Weights: `w_s`, `w_n`, `w_l`, `w_e` (sum to `1.0`).
- Half-life: `half_life_days` for decay.
- Target daily income default: `$200`.

Core formulas:
- `decay(days_ago) = 0.5^(days_ago / half_life_days)`
- `S = 1 - exp(-2.0 * S_raw)` where `S_raw` from decayed positive `(H,E)` signal.
- `N = 1 - exp(-0.6 * N_raw)` from decayed network exposure events.
- `L = 1 - exp(-0.7 * L_raw)` from decayed lead exposure events.
- `E_raw` from decayed `E` score mapped to `[0..1]`; apply variance penalty.
- `Readiness = 100 * clamp01(w_s*S + w_n*N + w_l*L + w_e*E)`.
- `confidence = clamp01(log(1 + days_with_any_logs)/log(31))`.

Defaults:
- `target_daily_income=200`, weights `0.25` each, `half_life_days=21`, `exposure_goal_per_week=5`.

### 3) API changes
New:
- `GET /api/income-model/settings`
- `PUT /api/income-model/settings`
- `GET /api/income-model/series?start=YYYY-MM-DD&end=YYYY-MM-DD`

Updated:
- `GET /api/analytics/summary` now includes `readiness_latest`, `capitals_latest`, `confidence_latest`.

Examples:
```bash
curl http://localhost:8000/api/income-model/settings

curl -X PUT http://localhost:8000/api/income-model/settings \
  -H "Content-Type: application/json" \
  -d '{
    "target_daily_income": 200,
    "w_s": 0.35,
    "w_n": 0.20,
    "w_l": 0.30,
    "w_e": 0.15,
    "half_life_days": 21,
    "exposure_goal_per_week": 5
  }'

curl "http://localhost:8000/api/income-model/series?start=2026-01-01&end=2026-01-31"
```

### 4) UI changes
- Dashboard: added “Target Readiness” KPI (+ confidence), readiness trend chart, and capital breakdown panel.
- New page “Income Model”: edit target and weights with auto-rebalancing sliders, half-life and exposure goal controls, live readiness preview.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
pytest -q
```
