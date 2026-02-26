from __future__ import annotations

from datetime import date, datetime

from app.analytics import compute_summary
from app.models import Action, Exposure


def mk_action(day: str, o_delta: int, r: int) -> Action:
    occurred = datetime.fromisoformat(f"{day}T12:00:00")
    return Action(
        occurred_at=occurred,
        domain="income",
        title="x",
        notes=None,
        h=0,
        r=r,
        d=0,
        e=0,
        o_delta=o_delta,
        tags=None,
    )


def mk_exposure(day: str) -> Exposure:
    return Exposure(occurred_at=datetime.fromisoformat(f"{day}T09:00:00"), type="post", notes=None)


def test_compute_summary_empty():
    summary = compute_summary([], [], start=date(2024, 1, 1), end=date(2024, 1, 3))
    assert summary.totals.sum_o_delta == 0
    assert summary.totals.constraint_debt_7d_last == 0
    assert len(summary.daily) == 3
    assert summary.weekly_exposure == []


def test_compute_summary_rolling_and_cumulative():
    actions = [
        mk_action("2024-01-01", 3, 1),
        mk_action("2024-01-02", -2, 0),
        mk_action("2024-01-03", -1, -1),
        mk_action("2024-01-08", -4, 2),
    ]
    exposures = [mk_exposure("2024-01-02"), mk_exposure("2024-01-08")]
    summary = compute_summary(actions, exposures, start=date(2024, 1, 1), end=date(2024, 1, 8))

    assert summary.daily[0].cumulative == 3
    assert summary.daily[2].cumulative == 0
    assert summary.daily[-1].constraint_debt_7d == -7
    assert summary.totals.sum_o_delta == -4
    assert summary.totals.exposure_count_period == 2


def test_irreversibility_average_per_day():
    actions = [mk_action("2024-01-01", 0, -2), mk_action("2024-01-01", 0, 2)]
    summary = compute_summary(actions, [], start=date(2024, 1, 1), end=date(2024, 1, 1))
    assert summary.daily[0].irreversibility_avg == 2.0
