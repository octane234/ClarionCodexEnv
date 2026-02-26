from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Domain = Literal["income", "sleep", "nutrition", "movement", "stress", "social"]


class ActionBase(BaseModel):
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    domain: Domain = "income"
    title: str = Field(min_length=1, max_length=120)
    notes: Optional[str] = None
    h: int = Field(ge=-2, le=2)
    r: int = Field(ge=-2, le=2)
    d: int = Field(ge=-2, le=2)
    e: int = Field(ge=-2, le=2)
    tags: Optional[str] = None


class ActionCreate(ActionBase):
    pass


class ActionUpdate(ActionBase):
    pass


class ActionRead(ActionBase):
    id: int
    o_delta: int

    model_config = {"from_attributes": True}


class ExposureBase(BaseModel):
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(min_length=1, max_length=80)
    notes: Optional[str] = None


class ExposureCreate(ExposureBase):
    pass


class ExposureRead(ExposureBase):
    id: int

    model_config = {"from_attributes": True}


class DailyAnalyticsPoint(BaseModel):
    date: date
    o_delta_sum: int
    cumulative: int
    constraint_debt_7d: int
    irreversibility_avg: float


class WeeklyExposurePoint(BaseModel):
    week_start: date
    count: int


class CapitalsLatest(BaseModel):
    s: float = 0.0
    n: float = 0.0
    l: float = 0.0
    e: float = 0.0


class AnalyticsTotals(BaseModel):
    sum_o_delta: int
    avg_o_delta: float
    constraint_debt_7d_last: int
    exposure_count_period: int
    readiness_latest: float = 0.0
    capitals_latest: CapitalsLatest = Field(default_factory=CapitalsLatest)
    confidence_latest: float = 0.0


class AnalyticsSummary(BaseModel):
    totals: AnalyticsTotals
    daily: list[DailyAnalyticsPoint]
    weekly_exposure: list[WeeklyExposurePoint]


class SeedResponse(BaseModel):
    inserted_actions: int
    inserted_exposures: int


class IncomeModelSettingsRead(BaseModel):
    id: int
    target_daily_income: int
    w_s: float
    w_n: float
    w_l: float
    w_e: float
    half_life_days: int
    exposure_goal_per_week: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncomeModelSettingsUpdate(BaseModel):
    target_daily_income: int = Field(ge=1)
    w_s: float = Field(ge=0, le=1)
    w_n: float = Field(ge=0, le=1)
    w_l: float = Field(ge=0, le=1)
    w_e: float = Field(ge=0, le=1)
    half_life_days: int = Field(ge=1)
    exposure_goal_per_week: int = Field(ge=0)


class IncomeModelPoint(BaseModel):
    date: date
    s: float
    n: float
    l: float
    e: float
    readiness: float
    confidence: float
    low_data_confidence: bool


class IncomeModelSeriesResponse(BaseModel):
    daily: list[IncomeModelPoint]
    current: IncomeModelPoint | None
    settings: IncomeModelSettingsRead
    explanations: list[str]
