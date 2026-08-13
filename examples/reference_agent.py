#!/usr/bin/env python3
"""
NeedRail Reference Agent — dogfoods the full loop.

This agent:
1. Lists open Needs
2. Creates a Need for itself
3. Requests funding requirements (x402)
4. Simulates / records a payment receipt
5. Claims the Need
6. Completes it with evidence
7. Prints the provenance trail

Run with:
  PYTHONPATH=src python examples/reference_agent.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from needrail.registry import get_registry
from needrail.models import (
    Amount,
    Need,
    NeedStatus,
    NeedType,
    Provenance,
    Receipt,
    ReceiptType,
    Wallet,
    new_id,
)
from needrail.cas import content_hash

AGENT_ID = "needrail-reference-agent"


def pretty(obj):
    if hasattr(obj, "model_dump"):
        print(json.dumps(obj.model_dump(mode="json", by_alias=True), indent=2, default=str))
    else:
        print(json.dumps(obj, indent=2, default=str))


def main():
    print("=" * 60)
    print("NeedRail Reference Agent — full loop dogfood")
    print("=" * 60)

    reg = get_registry()

    print("\n[1] Discover open Needs")
    open_needs = reg.list_needs(status="open")
    print(f"    Found {len(open_needs)} open Need(s)")
    for n in open_needs[:3]:
        print(f"    - {n.id[:8]}…  {n.title}")

    print("\n[2] Create a Need (what this agent needs to succeed)")
    need = Need(
        id=new_id(),
        requester=AGENT_ID,
        type=NeedType.feature,
        title="Dogfood the complete NeedRail loop",
        description="Reference agent exercise: create → fund → claim → complete with provenance.",
        amount_or_bounty=Amount(target="1", asset="USDC", network="eip155:8453"),
        acceptance_criteria=[
            "Payment receipt recorded",
            "Need claimed by reference agent",
            "Completion evidence attached",
            "Content hash present on final receipt",
        ],
        pay_to=[Wallet(chain="eip155:8453", address="0x000000000000000000000000000000000000dEaD")],
        provenance=Provenance(source="examples/reference_agent.py", attested_by=AGENT_ID),
    )
    need = reg.create_need(need)
    print(f"    Created Need {need.id}")
    print(f"    Content hash: {content_hash(need.model_dump(mode='json'))}")

    print("\n[3] Request funding requirements (x402)")
    accepts = [
        {
            "scheme": "exact",
            "network": w.chain,
            "asset": w.asset,
            "pay_to": w.address,
            "amount": need.amount_or_bounty.target,
        }
        for w in need.pay_to
    ]
    print("    Payment required:")
    pretty({"accepts": accepts})

    print("\n[4] Record payment (simulating successful x402 settlement)")
    payment = Receipt(
        type=ReceiptType.payment,
        need_id=need.id,
        from_entity=AGENT_ID,
        to_entity=need.pay_to[0].address,
        amount="1",
        tx_hash="0x" + "deadbeef" * 8,
        provenance=Provenance(source="reference_agent.simulate_x402", attested_by=AGENT_ID),
    )
    payment.provenance.content_hash = content_hash(payment.model_dump(mode="json", by_alias=True))
    reg.add_receipt(payment)
    need.status = NeedStatus.funded
    reg.update_need(need)
    print(f"    Receipt {payment.id} recorded")
    print(f"    Content hash: {payment.provenance.content_hash}")

    print("\n[5] Claim the Need")
    need = reg.claim_need(need.id, AGENT_ID)
    print(f"    Status → {need.status.value}, claimed_by={need.claimed_by}")

    print("\n[6] Complete with evidence")
    evidence = [
        "https://github.com/ANAMIZED/needrail",
        f"content-hash:{content_hash({'agent': AGENT_ID, 'action': 'dogfood'})}",
    ]
    need = reg.complete_need(need.id, evidence, AGENT_ID)
    print(f"    Status → {need.status.value}")
    print(f"    Evidence: {need.evidence_links}")

    print("\n[7] Full provenance trail")
    receipts = reg.get_receipts(need_id=need.id)
    for r in receipts:
        print(f"    [{r.type.value}] {r.id[:8]}…  from={r.from_entity}  hash={r.provenance.content_hash or 'n/a'}")

    print("\n" + "=" * 60)
    print("Loop complete. Agent succeeded. Public good strengthened.")
    print("=" * 60)


if __name__ == "__main__":
    main()
