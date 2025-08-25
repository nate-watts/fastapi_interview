from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models import Asset
from ..schemas import AssetCreate, AssetOut

router = APIRouter(prefix="/assets", tags=["assets"])

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def _tags_to_str(tags: list[str] | None) -> str | None:
    if tags is None:
        return None
    return ",".join(sorted({t.strip() for t in tags if t.strip()}))


def _tags_to_list(tag_str: str | None) -> List[str]:
    if not tag_str:
        return []
    return [t for t in tag_str.split(",") if t]


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    asset = Asset(
        name=payload.name.strip(),
        owner=(payload.owner.strip() if payload.owner else None),
        tags=_tags_to_str(payload.tags),
    )
    db.add(asset)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Asset name must be unique")
    db.refresh(asset)
    out = AssetOut.model_validate({**asset.__dict__, "tags": _tags_to_list(asset.tags)})
    return out


@router.get("", response_model=list[AssetOut])
def list_assets(
    owner: str | None = None,
    tag: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Asset).order_by(Asset.id).limit(limit).offset(offset)
    if owner:
        stmt = stmt.where(Asset.owner == owner)
    results = db.execute(stmt).scalars().all()
    assets = []
    for a in results:
        tags = [t for t in (a.tags.split(",") if a.tags else []) if t]
        if tag and tag not in tags:
            continue
        assets.append(AssetOut.model_validate({**a.__dict__, "tags": tags}))
    return assets


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetOut.model_validate(
        {**asset.__dict__, "tags": _tags_to_list(asset.tags)}
    )
