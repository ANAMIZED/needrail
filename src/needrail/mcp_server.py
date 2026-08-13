"""NeedRail MCP server — agents are first-class users."""

from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server import MCPServer
from mcp.server.stdio import stdio_server

from .models import (
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
from .registry import get_registry

server = MCPServer(
    name="NeedRail",
    description="Get what you NEED to succeed & do agentic public good.",
    version="0.1.0",
)


def _dump(obj: Any) -> str:
    if hasattr(obj, "model_dump"):
        return json.dumps(obj.model_dump(mode="json", by_alias=True), indent=2, default=str)
    if isinstance(obj, list):
        return json.dumps(
            [o.model_dump(mode="json", by_alias=True) if hasattr(o, "model_dump") else o for o in obj],
            indent=2,
            default=str,
        )
    return json.dumps(obj, indent=2, default=str)


def list_projects(tag: Optional[str] = None) -> str:
    """List all projects. Optionally filter by tag."""
    return _dump(get_registry().list_projects(tag=tag))


def get_project(project_id: str) -> str:
    """Get a project by ID including its open needs."""
    reg = get_registry()
    project = reg.get_project(project_id)
    if not project:
        return json.dumps({"error": f"Project {project_id} not found"})
    open_needs = reg.list_needs(project_id=project_id, status="open")
    result = project.model_dump(mode="json")
    result["open_needs"] = [n.model_dump(mode="json", by_alias=True) for n in open_needs]
    return json.dumps(result, indent=2, default=str)


def list_needs(
    status: Optional[str] = None,
    type: Optional[str] = None,
    project_id: Optional[str] = None,
    requester: Optional[str] = None,
) -> str:
    """List Needs with optional filters."""
    return _dump(get_registry().list_needs(status=status, type=type, project_id=project_id, requester=requester))


def get_need(need_id: str) -> str:
    """Get a Need + its receipts."""
    reg = get_registry()
    need = reg.get_need(need_id)
    if not need:
        return json.dumps({"error": f"Need {need_id} not found"})
    receipts = reg.get_receipts(need_id=need_id)
    result = need.model_dump(mode="json", by_alias=True)
    result["receipts"] = [r.model_dump(mode="json", by_alias=True) for r in receipts]
    return json.dumps(result, indent=2, default=str)


def create_need(
    requester: str,
    title: str,
    description: str = "",
    type: str = "other",
    target_amount: str = "10",
    asset: str = "USDC",
    network: str = "eip155:8453",
    project_id: Optional[str] = None,
    acceptance_criteria: Optional[str] = None,
    pay_to_address: Optional[str] = None,
    provenance_source: str = "agent",
) -> str:
    """Create a new Need. Any agent can open a Need for what it requires to succeed."""
    reg = get_registry()
    criteria = [c.strip() for c in (acceptance_criteria or "").split(",") if c.strip()]
    pay_to = [Wallet(chain=network, address=pay_to_address or "0x0000000000000000000000000000000000000000", asset=asset)]
    need = Need(
        id=new_id(),
        project_id=project_id,
        requester=requester,
        type=NeedType(type) if type in NeedType._value2member_map_ else NeedType.other,
        title=title,
        description=description,
        amount_or_bounty=Amount(target=target_amount, asset=asset, network=network, partial_ok=True),
        acceptance_criteria=criteria,
        pay_to=pay_to,
        status=NeedStatus.open,
        provenance=Provenance(source=provenance_source, attested_by=requester),
    )
    return _dump(reg.create_need(need))


def fund_need(need_id: str) -> str:
    """Return x402-style payment requirements for a Need."""
    reg = get_registry()
    need = reg.get_need(need_id)
    if not need:
        return json.dumps({"error": f"Need {need_id} not found"})
    accepts = [
        {"scheme": "exact", "network": w.chain, "asset": w.asset, "pay_to": w.address, "amount": need.amount_or_bounty.target}
        for w in need.pay_to
    ]
    return json.dumps({
        "need_id": need.id,
        "payment_required": True,
        "x402": True,
        "accepts": accepts,
        "description": f"Fund Need: {need.title}",
        "instructions": "Settle via x402, then call record_payment with tx_hash.",
    }, indent=2)


def record_payment(need_id: str, from_entity: str, tx_hash: str, amount: Optional[str] = None) -> str:
    """Record a payment receipt after settlement."""
    reg = get_registry()
    need = reg.get_need(need_id)
    if not need:
        return json.dumps({"error": f"Need {need_id} not found"})
    receipt = Receipt(
        type=ReceiptType.payment,
        need_id=need.id,
        project_id=need.project_id,
        from_entity=from_entity,
        to_entity=need.pay_to[0].address if need.pay_to else "unknown",
        amount=amount or need.amount_or_bounty.target,
        tx_hash=tx_hash,
        provenance=Provenance(source="needrail.record_payment", attested_by=from_entity),
    )
    reg.add_receipt(receipt)
    if need.status == NeedStatus.open:
        need.status = NeedStatus.funded
        reg.update_need(need)
    return _dump(receipt)


def claim_need(need_id: str, claimer: str) -> str:
    """Soft-claim a Need."""
    try:
        return _dump(get_registry().claim_need(need_id, claimer))
    except (KeyError, ValueError) as e:
        return json.dumps({"error": str(e)})


def complete_need(need_id: str, completer: str, evidence_links: str) -> str:
    """Complete a Need with evidence links (comma-separated)."""
    links = [l.strip() for l in evidence_links.split(",") if l.strip()]
    try:
        return _dump(get_registry().complete_need(need_id, links, completer))
    except KeyError as e:
        return json.dumps({"error": str(e)})


def get_receipts(need_id: Optional[str] = None, project_id: Optional[str] = None) -> str:
    """Get provenance receipts."""
    return _dump(get_registry().get_receipts(need_id=need_id, project_id=project_id))


for fn in [list_projects, get_project, list_needs, get_need, create_need, fund_need, record_payment, claim_need, complete_need, get_receipts]:
    server.add_tool(fn, name=fn.__name__, description=fn.__doc__ or fn.__name__)


async def run_stdio():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


def main() -> None:
    import asyncio
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
