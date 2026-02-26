from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable

from .models import Action, Exposure
from .schemas import AnalyticsSummary, AnalyticsTotals, CapitalsLatest, DailyAnalyticsPoint, WeeklyExposurePoint


def _date_span(start: date, end: date) -> list[date]:
    day_count = (end - start).days + 1
    return [start + timedelta(days=offset) for offset in range(day_count)]


def compute_summary(
    actions: Iterable[Action],
    exposures: Iterable[Exposure],
    start: date,
    end: date,
    readiness_latest: float = 0.0,
    capitals_latest: CapitalsLatest | None = None,
    confidence_latest: float = 0.0,
) -> AnalyticsSummary:
    days = _date_span(start, end)

    by_day_o_delta: dict[date, int] = defaultdict(int)
    by_day_neg_delta: dict[date, int] = defaultdict(int)
    by_day_irreversibility_values: dict[date, list[float]] = defaultdict(list)

    for action in actions:
        day = action.occurred_at.date()
        by_day_o_delta[day] += action.o_delta
        by_day_neg_delta[day] += min(0, action.o_delta)
        by_day_irreversibility_values[day].append(float(2 - action.r))

    daily: list[DailyAnalyticsPoint] = []
    cumulative = 0
    for idx, day in enumerate(days):
        day_o_delta = by_day_o_delta[day]
        cumulative += day_o_delta
        window_days = days[max(0, idx - 6) : idx + 1]
        constraint_debt = sum(by_day_neg_delta[d] for d in window_days)
        iv = by_day_irreversibility_values.get(day, [])
        irreversibility_avg = sum(iv) / len(iv) if iv else 0.0
        daily.append(
            DailyAnalyticsPoint(
                date=day,
                o_delta_sum=day_o_delta,
                cumulative=cumulative,
                constraint_debt_7d=constraint_debt,
                irreversibility_avg=round(irreversibility_avg, 2),
            )
        )

    weekly_counts: dict[date, int] = defaultdict(int)
    for exposure in exposures:
        exp_day = exposure.occurred_at.date()
        week_start = exp_day - timedelta(days=exp_day.weekday())
        weekly_counts[week_start] += 1

    weekly_exposure = [
        WeeklyExposurePoint(week_start=week_start, count=count)
        for week_start, count in sorted(weekly_counts.items())
        if start <= week_start <= end or start <= week_start + timedelta(days=6) <= end
    ]

    sum_o_delta = sum(point.o_delta_sum for point in daily)
    totals = AnalyticsTotals(
        sum_o_delta=sum_o_delta,
        avg_o_delta=round(sum_o_delta / len(daily), 2) if daily else 0.0,
        constraint_debt_7d_last=daily[-1].constraint_debt_7d if daily else 0,
        exposure_count_period=sum(point.count for point in weekly_exposure),
        readiness_latest=round(readiness_latest, 2),
        capitals_latest=capitals_latest or CapitalsLatest(),
        confidence_latest=round(confidence_latest, 4),
    )
    return AnalyticsSummary(totals=totals, daily=daily, weekly_exposure=weekly_exposure)
