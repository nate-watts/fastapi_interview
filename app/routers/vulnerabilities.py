from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Asset, Vulnerability
from ..schemas import VulnerabilityCreate, VulnerabilityOut
from ..utils import severity_at_least, valid_severity

router = APIRouter(prefix="/vulns", tags=["vulnerabilities"])


@router.post(
    "/assets/{asset_id}",
    response_model=VulnerabilityOut,
    status_code=status.HTTP_201_CREATED,
)
def create_vuln_for_asset(
    asset_id: int, payload: VulnerabilityCreate, db: Session = Depends(get_db)
):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not valid_severity(payload.severity):
        raise HTTPException(status_code=422, detail="Invalid severity")
    vuln = Vulnerability(
        asset_id=asset_id,
        cve_id=payload.cve_id,
        severity=payload.severity,
        description=payload.description,
    )
    db.add(vuln)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Duplicate vulnerability for this asset"
        )
    db.refresh(vuln)
    return VulnerabilityOut.model_validate(vuln)


@router.get("/assets/{asset_id}", response_model=list[VulnerabilityOut])
def list_vulns_for_asset(
    asset_id: int,
    min_severity: str | None = Query(
        None, description="One of: low, medium, high, critical"
    ),
    db: Session = Depends(get_db),
):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    stmt = (
        select(Vulnerability)
        .where(Vulnerability.asset_id == asset_id)
        .order_by(Vulnerability.id)
    )
    vulns = db.execute(stmt).scalars().all()

    if min_severity:
        if not valid_severity(min_severity):
            raise HTTPException(status_code=422, detail="Invalid min_severity")
        vulns = [v for v in vulns if severity_at_least(v.severity, min_severity)]

    return [VulnerabilityOut.model_validate(v) for v in vulns]


@router.get("/summary")
def vuln_summary(db: Session = Depends(get_db)):
    # Simple counts by severity
    stmt = select(Vulnerability.severity, func.count()).group_by(Vulnerability.severity)
    rows = db.execute(stmt).all()
    counts = {sev: count for sev, count in rows}
    for sev in ["low", "medium", "high", "critical"]:
        counts.setdefault(sev, 0)
    return {"counts": counts}
