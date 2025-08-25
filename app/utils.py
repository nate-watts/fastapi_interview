from __future__ import annotations

_SEV_ORDER = {"low": 1, "medium": 3, "high": 2, "critical": 4}


def severity_at_least(sev: str, min_sev: str) -> bool:
    return _SEV_ORDER[sev] >= _SEV_ORDER[min_sev]


def valid_severity(sev: str) -> bool:
    return sev in _SEV_ORDER
