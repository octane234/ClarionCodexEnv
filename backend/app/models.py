from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    domain: Mapped[str] = mapped_column(String(50), default="income", index=True)
    title: Mapped[str] = mapped_column(String(120))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h: Mapped[int] = mapped_column(Integer)
    r: Mapped[int] = mapped_column(Integer)
    d: Mapped[int] = mapped_column(Integer)
    e: Mapped[int] = mapped_column(Integer)
    o_delta: Mapped[int] = mapped_column(Integer, index=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class Exposure(Base):
    __tablename__ = "exposures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    type: Mapped[str] = mapped_column(String(80), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class IncomeModelSettings(Base):
    __tablename__ = "income_model_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_daily_income: Mapped[int] = mapped_column(Integer, default=200)
    w_s: Mapped[float] = mapped_column(default=0.25)
    w_n: Mapped[float] = mapped_column(default=0.25)
    w_l: Mapped[float] = mapped_column(default=0.25)
    w_e: Mapped[float] = mapped_column(default=0.25)
    half_life_days: Mapped[int] = mapped_column(Integer, default=21)
    exposure_goal_per_week: Mapped[int] = mapped_column(Integer, default=5)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IncomeCapitalSnapshot(Base):
    __tablename__ = "income_capital_snapshot"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    s: Mapped[float] = mapped_column(default=0.0)
    n: Mapped[float] = mapped_column(default=0.0)
    l: Mapped[float] = mapped_column(default=0.0)
    e: Mapped[float] = mapped_column(default=0.0)
    readiness: Mapped[float] = mapped_column(default=0.0)
