"""Evidence-weighted reputation surface (Phase 2). Counts only — no composite score."""

from __future__ import annotations
from typing import Any, Iterable
from .registry import Registry


def _iter_needs(reg: Registry) -> Iterable:
    needs = getattr(reg, "needs", None)
    if needs is None:
        return []
    if isinstance(needs, dict):
        return needs.values()
    return needs


def reputation_for(agent_ref: str, reg: Registry) -> dict[str, Any]:
    completed = 0
    value = 0.0
    independent = 0
    for need in _iter_needs(reg):
        status = getattr(need.status, "value", need.status)
        if status == "completed":
            if need.claimed_by == agent_ref or need.requester == agent_ref:
                completed += 1
                try:
                    value += float(need.amount_or_bounty.target)
                except Exception:
                    pass
    for r in getattr(reg, "receipts", []) or []:
        att = (r.provenance.attested_by if r.provenance else None) or ""
        rtype = getattr(r.type, "value", r.type)
        if rtype in ("completion", "payment") and att and att != agent_ref:
            if r.from_entity == agent_ref or r.to_entity == agent_ref:
                independent += 1
    return {
        "agent": agent_ref,
        "completed_count": completed,
        "total_value_usdc": round(value, 2),
        "independent_attestation_count": independent,
        "note": "counts and value only — no composite score",
    }
