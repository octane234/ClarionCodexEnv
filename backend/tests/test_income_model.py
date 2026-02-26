from __future__ import annotations

from datetime import date, datetime

from fastapi.testclient import TestClient

from app.income_model import clamp01, compute_income_series, decay_factor, saturate
from app.main import app
from app.models import Action, Exposure, IncomeModelSettings


def test_decay_factor_half_life():
    assert decay_factor(0, 21) == 1.0
    assert round(decay_factor(21, 21), 6) == 0.5


def test_saturation_monotonic_bounded():
    a = saturate(0.1, 0.7)
    b = saturate(1.0, 0.7)
    c = saturate(4.0, 0.7)
    assert 0 <= a <= 1
    assert 0 <= b <= 1
    assert 0 <= c <= 1
    assert a < b < c


def test_low_data_defaults_and_confidence():
    settings = IncomeModelSettings(
        id=1,
        target_daily_income=200,
        w_s=0.25,
        w_n=0.25,
        w_l=0.25,
        w_e=0.25,
        half_life_days=21,
        exposure_goal_per_week=5,
        updated_at=datetime.utcnow(),
    )
    points = compute_income_series([], [], date(2024, 1, 1), date(2024, 1, 2), settings)
    assert points[-1].low_data_confidence is True
    assert points[-1].confidence == 0.0
    assert 0 <= points[-1].readiness <= 100


def test_weight_sum_validation_endpoint():
    client = TestClient(app)
    res = client.put(
        "/api/income-model/settings",
        json={
            "target_daily_income": 200,
            "w_s": 0.4,
            "w_n": 0.4,
            "w_l": 0.4,
            "w_e": 0.1,
            "half_life_days": 21,
            "exposure_goal_per_week": 5,
        },
    )
    assert res.status_code == 400



def test_clamp01():
    assert clamp01(-1) == 0
    assert clamp01(0.3) == 0.3
    assert clamp01(9) == 1
