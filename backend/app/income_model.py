from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

from .models import Action, Exposure, IncomeModelSettings

NETWORK_TYPES = {"outreach", "interview", "proposal", "post", "portfolio_update"}
LEAD_TYPES = {"application", "outreach", "proposal", "post"}
ENERGY_DOMAINS = {"sleep", "nutrition", "movement", "stress"}


@dataclass
class IncomePoint:
    date: date
    s: float
    n: float
    l: float
    e: float
    readiness: float
    confidence: float
    low_data_confidence: bool


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def decay_factor(days_ago: int, half_life_days: int) -> float:
    return 0.5 ** (days_ago / max(1, half_life_days))


def saturate(raw: float, k: float) -> float:
    return clamp01(1 - math.exp(-k * max(0.0, raw)))


def _daterange(start: date, end: date) -> list[date]:
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def _weighted_avg(values: list[tuple[float, float]]) -> float:
    if not values:
        return 0.0
    num = sum(v * w for v, w in values)
    den = sum(w for _, w in values)
    return num / den if den else 0.0


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)


def get_or_create_settings(db, now: datetime | None = None) -> IncomeModelSettings:
    settings = db.get(IncomeModelSettings, 1)
    if settings:
        return settings
    settings = IncomeModelSettings(
        id=1,
        target_daily_income=200,
        w_s=0.25,
        w_n=0.25,
        w_l=0.25,
        w_e=0.25,
        half_life_days=21,
        exposure_goal_per_week=5,
        updated_at=now or datetime.utcnow(),
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def compute_income_series(
    actions: Iterable[Action],
    exposures: Iterable[Exposure],
    start: date,
    end: date,
    settings: IncomeModelSettings,
    window_days: int = 60,
) -> list[IncomePoint]:
    actions_list = list(actions)
    exposures_list = list(exposures)
    all_days = _daterange(start, end)

    points: list[IncomePoint] = []
    for day in all_days:
        window_start = day - timedelta(days=window_days - 1)

        skill_weighted: list[tuple[float, float]] = []
        network_raw = 0.0
        lead_raw = 0.0
        energy_weighted: list[tuple[float, float]] = []
        energy_daily: dict[date, list[float]] = defaultdict(list)
        days_with_any_logs: set[date] = set()

        for a in actions_list:
            ad = a.occurred_at.date()
            if ad < window_start or ad > day:
                continue
            days_ago = (day - ad).days
            decay = decay_factor(days_ago, settings.half_life_days)
            days_with_any_logs.add(ad)

            skill_contrib = clamp01((max(0, a.h) + max(0, a.e)) / 4)
            skill_weighted.append((skill_contrib, decay))

            energy_signal = clamp01((a.e + 2) / 4)
            energy_weighted.append((energy_signal, decay))
            energy_daily[ad].append(energy_signal)

        for ex in exposures_list:
            ed = ex.occurred_at.date()
            if ed < window_start or ed > day:
                continue
            days_ago = (day - ed).days
            decay = decay_factor(days_ago, settings.half_life_days)
            days_with_any_logs.add(ed)
            et = ex.type.lower().strip()
            if et in NETWORK_TYPES:
                network_raw += decay
            if et in LEAD_TYPES:
                lead_raw += decay

        s_raw = _weighted_avg(skill_weighted)
        s = saturate(s_raw, 2.0)
        n = saturate(network_raw, 0.6)
        l = saturate(lead_raw, 0.7)

        e_raw = _weighted_avg(energy_weighted)
        daily_energy_means = [sum(vs) / len(vs) for vs in energy_daily.values()]
        var_penalty = clamp01(_variance(daily_energy_means) / 0.05)
        e = clamp01(e_raw * (1 - 0.5 * var_penalty))

        low_data = len(days_with_any_logs) < 5
        if low_data:
            s = s if s > 0 else 0.5
            n = n if n > 0 else 0.5
            l = l if l > 0 else 0.5
            e = e if e > 0 else 0.5

        readiness = 100 * clamp01(settings.w_s * s + settings.w_n * n + settings.w_l * l + settings.w_e * e)
        confidence = clamp01(math.log(1 + len(days_with_any_logs)) / math.log(1 + 30))

        points.append(
            IncomePoint(
                date=day,
                s=round(s, 4),
                n=round(n, 4),
                l=round(l, 4),
                e=round(e, 4),
                readiness=round(readiness, 2),
                confidence=round(confidence, 4),
                low_data_confidence=low_data,
            )
        )

    return points
