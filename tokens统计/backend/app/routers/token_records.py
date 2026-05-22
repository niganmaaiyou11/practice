from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.auth import get_current_user
from app.models import User
from app.schemas import (
    TokenUsageCreate,
    TokenUsageUpdate,
    TokenUsageResponse,
    PaginatedResponse,
    DailySummary,
    ModelBreakdown,
    ProviderBreakdown,
    Totals,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/records", response_model=PaginatedResponse)
def list_records(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    model_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records, total = crud.get_records(db, skip, limit, start_date, end_date, provider, model_name)
    return PaginatedResponse(
        records=[TokenUsageResponse.model_validate(r) for r in records],
        total=total,
    )


@router.get("/records/{record_id}", response_model=TokenUsageResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = crud.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return TokenUsageResponse.model_validate(record)


@router.post("/records", response_model=TokenUsageResponse, status_code=201)
def create_record(
    data: TokenUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = crud.create_record(db, data, user_id=current_user.id)
    return TokenUsageResponse.model_validate(record)


@router.put("/records/{record_id}", response_model=TokenUsageResponse)
def update_record(
    record_id: int,
    data: TokenUsageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = crud.update_record(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return TokenUsageResponse.model_validate(record)


@router.delete("/records/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = crud.delete_record(db, record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")


@router.get("/summary/daily", response_model=list[DailySummary])
def daily_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [DailySummary(**row) for row in crud.get_daily_summary(db, start_date, end_date, provider)]


@router.get("/summary/by-model", response_model=list[ModelBreakdown])
def model_breakdown(
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [ModelBreakdown(**row) for row in crud.get_model_breakdown(db, start_date, end_date, provider)]


@router.get("/summary/by-provider", response_model=list[ProviderBreakdown])
def provider_breakdown(
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [ProviderBreakdown(**row) for row in crud.get_provider_breakdown(db, start_date, end_date, provider)]


@router.get("/summary/totals", response_model=Totals)
def totals(
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return Totals(**crud.get_totals(db, start_date, end_date, provider))
