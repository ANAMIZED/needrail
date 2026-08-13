#!/usr/bin/env python3
"""Seed the NeedRail Python registry from a client export (needrail-registry.json)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from needrail.models import (
    Amount, Need, NeedStatus, NeedType, Project, Provenance,
    Receipt, ReceiptType, Wallet,
)
from needrail.registry import get_registry


def main() -> None:
    ap = argparse.ArgumentParser(description="Import NeedRail client JSON into the node registry")
    ap.add_argument("export", type=Path, help="Path to needrail-registry.json")
    args = ap.parse_args()

    data = json.loads(args.export.read_text())
    if data.get("spec") != "needrail/v1":
        print("Warning: spec is not needrail/v1 — continuing anyway", file=sys.stderr)

    reg = get_registry()
    np = nn = nr = 0

    for p in data.get("projects") or []:
        if hasattr(reg, "get_project") and reg.get_project(p["id"]):
            continue
        if getattr(reg, "projects", None) and p["id"] in reg.projects:
            continue
        proj = Project(
            id=p["id"],
            name=p.get("name") or p["id"],
            description=p.get("description") or "",
            repository=p.get("repository"),
            license=p.get("license"),
            tags=p.get("tags") or [],
            provenance=Provenance(source="client-import"),
        )
        if hasattr(reg, "create_project"):
            reg.create_project(proj)
        else:
            reg.projects[proj.id] = proj
            if hasattr(reg, "_persist"):
                try:
                    reg._persist()
                except OSError:
                    pass
        np += 1
        print(f"  project {proj.id}  {proj.name}")

    valid_types = set(NeedType.__members__)
    for n in data.get("needs") or []:
        if reg.get_need(n["id"]):
            continue
        t = n.get("type") or "other"
        if t not in valid_types:
            t = "other"
        ab = n.get("amount_or_bounty") or {}
        pay = [
            Wallet(chain=w.get("chain", "eip155:8453"), address=w["address"])
            for w in (n.get("pay_to") or [])
            if w.get("address")
        ]
        st = n.get("status") or "open"
        try:
            status = NeedStatus(st)
        except ValueError:
            status = NeedStatus.open
        need = Need(
            id=n["id"],
            project_id=n.get("project_id"),
            requester=n.get("requester") or "imported",
            type=NeedType(t),
            title=n.get("title") or n["id"],
            description=n.get("description") or "",
            amount_or_bounty=Amount(
                target=str(ab.get("target") or "0"),
                asset=ab.get("asset") or "USDC",
                network=ab.get("network") or "eip155:8453",
                partial_ok=bool(ab.get("partial_ok")),
            ),
            acceptance_criteria=n.get("acceptance_criteria") or [],
            pay_to=pay,
            status=status,
            claimed_by=n.get("claimed_by"),
            evidence_links=n.get("evidence_links") or [],
            provenance=Provenance(
                source="client-import",
                attested_by=n.get("requester"),
                content_hash=n.get("content_hash"),
            ),
        )
        reg.create_need(need)
        nn += 1
        print(f"  need {need.id}  {need.title}")

    for r in data.get("receipts") or []:
        rid = r.get("id")
        if rid and any(getattr(x, "id", None) == rid for x in reg.receipts):
            continue
        try:
            rtype = ReceiptType(r.get("type") or "payment")
        except ValueError:
            rtype = ReceiptType.payment
        rec = Receipt(
            type=rtype,
            need_id=r.get("need_id"),
            project_id=r.get("project_id"),
            from_entity=r.get("from") or r.get("from_entity") or "imported",
            to_entity=r.get("to") or r.get("to_entity") or "",
            amount=r.get("amount"),
            tx_hash=r.get("tx_hash"),
            evidence=r.get("evidence") or [],
            provenance=Provenance(source="client-import", content_hash=r.get("content_hash")),
        )
        if rid:
            rec.id = rid
        reg.add_receipt(rec)
        nr += 1
        print(f"  receipt {rec.id}  {rec.type.value}")

    print(f"Imported {np} projects, {nn} needs, {nr} receipts")
    print("Start the node: uvicorn needrail.server:app --reload")
    print("Then open /needs/{id}/fund for HTTP 402.")


if __name__ == "__main__":
    main()
