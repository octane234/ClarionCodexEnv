from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .analytics import compute_summary
from .database import Base, engine, get_db
from .income_model import compute_income_series, get_or_create_settings
from .models import Action, Exposure
from .schemas import (
    ActionCreate,
    ActionRead,
    ActionUpdate,
    AnalyticsSummary,
    CapitalsLatest,
    ExposureCreate,
    ExposureRead,
    IncomeModelSeriesResponse,
    IncomeModelSettingsRead,
    IncomeModelSettingsUpdate,
    IncomeModelPoint,
    SeedResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Optionality Tracker API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/actions", response_model=ActionRead)
def create_action(payload: ActionCreate, db: Session = Depends(get_db)) -> Action:
    action = Action(
        occurred_at=payload.occurred_at,
        domain=payload.domain,
        title=payload.title,
        notes=payload.notes,
        h=payload.h,
        r=payload.r,
        d=payload.d,
        e=payload.e,
        o_delta=payload.h + payload.r - payload.d + payload.e,
        tags=payload.tags,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@app.get("/api/actions", response_model=list[ActionRead])
def list_actions(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(Action)
    if start:
        query = query.where(Action.occurred_at >= datetime.combine(start, datetime.min.time()))
    if end:
        query = query.where(Action.occurred_at < datetime.combine(end + timedelta(days=1), datetime.min.time()))
    return list(db.scalars(query.order_by(Action.occurred_at.desc()).limit(limit).offset(offset)).all())


@app.get("/api/actions/{action_id}", response_model=ActionRead)
def get_action(action_id: int, db: Session = Depends(get_db)) -> Action:
    action = db.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@app.put("/api/actions/{action_id}", response_model=ActionRead)
def update_action(action_id: int, payload: ActionUpdate, db: Session = Depends(get_db)) -> Action:
    action = db.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    for field in ["occurred_at", "domain", "title", "notes", "h", "r", "d", "e", "tags"]:
        setattr(action, field, getattr(payload, field))
    action.o_delta = payload.h + payload.r - payload.d + payload.e
    db.commit()
    db.refresh(action)
    return action


@app.delete("/api/actions/{action_id}")
def delete_action(action_id: int, db: Session = Depends(get_db)) -> dict[str, bool]:
    action = db.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    db.delete(action)
    db.commit()
    return {"deleted": True}


@app.post("/api/exposures", response_model=ExposureRead)
def create_exposure(payload: ExposureCreate, db: Session = Depends(get_db)) -> Exposure:
    exposure = Exposure(occurred_at=payload.occurred_at, type=payload.type, notes=payload.notes)
    db.add(exposure)
    db.commit()
    db.refresh(exposure)
    return exposure


@app.get("/api/exposures", response_model=list[ExposureRead])
def list_exposures(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Exposure)
    if start:
        query = query.where(Exposure.occurred_at >= datetime.combine(start, datetime.min.time()))
    if end:
        query = query.where(Exposure.occurred_at < datetime.combine(end + timedelta(days=1), datetime.min.time()))
    return list(db.scalars(query.order_by(Exposure.occurred_at.desc())).all())


@app.delete("/api/exposures/{exposure_id}")
def delete_exposure(exposure_id: int, db: Session = Depends(get_db)) -> dict[str, bool]:
    exposure = db.get(Exposure, exposure_id)
    if not exposure:
        raise HTTPException(status_code=404, detail="Exposure not found")
    db.delete(exposure)
    db.commit()
    return {"deleted": True}


@app.get("/api/income-model/settings", response_model=IncomeModelSettingsRead)
def get_income_model_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)


@app.put("/api/income-model/settings", response_model=IncomeModelSettingsRead)
def update_income_model_settings(payload: IncomeModelSettingsUpdate, db: Session = Depends(get_db)):
    total = payload.w_s + payload.w_n + payload.w_l + payload.w_e
    if abs(total - 1.0) > 1e-3:
        raise HTTPException(status_code=400, detail="weights must sum to 1.0")
    settings = get_or_create_settings(db)
    for field in ["target_daily_income", "w_s", "w_n", "w_l", "w_e", "half_life_days", "exposure_goal_per_week"]:
        setattr(settings, field, getattr(payload, field))
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    return settings


@app.get("/api/income-model/series", response_model=IncomeModelSeriesResponse)
def income_model_series(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    end_date = end or date.today()
    start_date = start or (end_date - timedelta(days=29))
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end must be on or after start")

    settings = get_or_create_settings(db)
    fetch_start = datetime.combine(start_date - timedelta(days=59), datetime.min.time())
    fetch_end = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    actions = list(db.scalars(select(Action).where(Action.occurred_at >= fetch_start, Action.occurred_at < fetch_end)).all())
    exposures = list(db.scalars(select(Exposure).where(Exposure.occurred_at >= fetch_start, Exposure.occurred_at < fetch_end)).all())

    points = compute_income_series(actions, exposures, start_date, end_date, settings)
    daily = [IncomeModelPoint(**p.__dict__) for p in points]
    explanations = [
        "S uses decayed positive H and E from actions, then saturation.",
        "N uses decayed network-oriented exposures: outreach/interview/proposal/post/portfolio_update.",
        "L uses decayed lead-oriented exposures: application/outreach/proposal/post.",
        "E uses decayed E score signal with variance penalty for stability.",
    ]
    return IncomeModelSeriesResponse(
        daily=daily,
        current=daily[-1] if daily else None,
        settings=IncomeModelSettingsRead.model_validate(settings),
        explanations=explanations,
    )


@app.get("/api/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    end_date = end or date.today()
    start_date = start or (end_date - timedelta(days=29))
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end must be on or after start")

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    actions = list(db.scalars(select(Action).where(Action.occurred_at >= start_dt, Action.occurred_at < end_dt)).all())
    exposures = list(db.scalars(select(Exposure).where(Exposure.occurred_at >= start_dt, Exposure.occurred_at < end_dt)).all())

    settings = get_or_create_settings(db)
    income_points = compute_income_series(actions, exposures, start_date, end_date, settings)
    latest = income_points[-1] if income_points else None
    capitals = CapitalsLatest(s=latest.s, n=latest.n, l=latest.l, e=latest.e) if latest else CapitalsLatest()
    return compute_summary(
        actions=actions,
        exposures=exposures,
        start=start_date,
        end=end_date,
        readiness_latest=latest.readiness if latest else 0.0,
        capitals_latest=capitals,
        confidence_latest=latest.confidence if latest else 0.0,
    )


@app.post("/api/dev/seed", response_model=SeedResponse)
def seed_demo_data(db: Session = Depends(get_db)) -> SeedResponse:
    now = datetime.utcnow()
    domains = ["income", "sleep", "nutrition", "movement", "stress", "social"]
    exposure_types = ["application", "outreach", "post", "proposal", "interview", "portfolio_update"]

    for i in range(20):
        h = (i % 5) - 2
        r = ((i + 1) % 5) - 2
        d = ((i + 2) % 5) - 2
        e = ((i + 3) % 5) - 2
        db.add(
            Action(
                occurred_at=now - timedelta(days=19 - i),
                domain=domains[i % len(domains)],
                title=f"Sample action {i + 1}",
                notes="Seeded demo action",
                h=h,
                r=r,
                d=d,
                e=e,
                o_delta=h + r - d + e,
                tags="demo,seed",
            )
        )

    for i in range(12):
        db.add(
            Exposure(
                occurred_at=now - timedelta(days=i * 2),
                type=exposure_types[i % len(exposure_types)],
                notes="Seeded demo exposure",
            )
        )

    db.commit()
    return SeedResponse(inserted_actions=20, inserted_exposures=12)
