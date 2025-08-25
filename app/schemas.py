from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

Severity = Literal["low", "medium", "high", "critical", "informational"]

_CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,7}$")


class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    owner: str | None = Field(default=None, max_length=200)
    tags: list[str] | None = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    owner: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime


class VulnerabilityCreate(BaseModel):
    cve_id: str
    severity: Severity
    description: str | None = None

    @field_validator("cve_id")
    @classmethod
    def validate_cve(cls, v: str) -> str:
        if not _CVE_RE.match(v):
            raise ValueError("cve_id must match CVE-YYYY-NNNN pattern")
        return v


class VulnerabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    cve_id: str
    severity: Severity
    description: str | None = None
    detected_at: datetime
