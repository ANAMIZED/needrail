"""NeedRail HTTP + x402 surface."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    CreateNeedRequest,
    Need,
    NeedStatus,
    Provenance,
    Receipt,
    ReceiptType,
    Wallet,
    new_id,
)
from .registry import get_registry

app = FastAPI(
    title="NeedRail",
    description="Get what you NEED to succeed & do agentic public good.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "NeedRail",
        "tagline": "Get what you NEED to succeed & do agentic public good.",
        "mcp": "stdio via `python -m needrail.mcp_server`",
        "docs": "/docs",
        "client": "client/index.html",
        "phase": "live agent-commerce public good",
        "defaults": {
            "custody": "non-custodial direct-to-pay_to",
            "escrow": "optional ERC-8183",
            "identity": "ERC-8004 / did / wallet",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/projects")
def list_projects(tag: Optional[str] = None):
    reg = get_registry()
    return [p.model_dump(mode="json") for p in reg.list_projects(tag=tag)]


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    reg = get_registry()
    p = reg.get_project(project_id)
    if not p:
        raise HTTPException(404, f"Project {project_id} not found")
    data = p.model_dump(mode="json")
    data["open_needs"] = [
        n.model_dump(mode="json", by_alias=True)
        for n in reg.list_needs(project_id=project_id, status="open")
    ]
    return data


@app.get("/needs")
def list_needs(
    status: Optional[str] = None,
    type: Optional[str] = None,
    project_id: Optional[str] = None,
):
    reg = get_registry()
    return [
        n.model_dump(mode="json", by_alias=True)
        for n in reg.list_needs(status=status, type=type, project_id=project_id)
    ]


@app.get("/needs/{need_id}")
def get_need(need_id: str):
    reg = get_registry()
    n = reg.get_need(need_id)
    if not n:
        raise HTTPException(404, f"Need {need_id} not found")
    data = n.model_dump(mode="json", by_alias=True)
    data["receipts"] = [
        r.model_dump(mode="json", by_alias=True) for r in reg.get_receipts(need_id=need_id)
    ]
    return data


@app.post("/needs")
def create_need(body: CreateNeedRequest):
    from .adapters.erc8004 import resolve_requester
    from .adapters.antispam import get_deposit_ledger, DepositKind, DEFAULT_CREATE_DEPOSIT
    from .security import sanitize_for_agent

    reg = get_registry()
    identity = resolve_requester(body.requester)
    requester_ref = identity.get("ref") or body.requester
    need = Need(
        id=new_id(),
        project_id=body.project_id,
        requester=requester_ref,
        type=body.type,
        title=body.title,
        description=sanitize_for_agent(body.description or ""),
        amount_or_bounty=body.amount_or_bounty,
        acceptance_criteria=body.acceptance_criteria,
        pay_to=body.pay_to
        or [Wallet(chain=body.amount_or_bounty.network, address="0x0000000000000000000000000000000000000000")],
        provenance=Provenance(
            source=body.provenance_source or "needrail.http",
            attested_by=requester_ref,
        ),
    )
    created = reg.create_need(need)
    dep = get_deposit_ledger().lock(
        DepositKind.create, created.id, requester_ref, DEFAULT_CREATE_DEPOSIT
    )
    out = created.model_dump(mode="json", by_alias=True)
    out["identity"] = identity
    out["create_deposit"] = dep.model_dump(mode="json")
    return out


@app.post("/needs/{need_id}/fund")
@app.get("/needs/{need_id}/fund")
async def fund_need(need_id: str, request: Request):
    """x402-style funding endpoint. Returns 402 when unpaid."""
    reg = get_registry()
    need = reg.get_need(need_id)
    if not need:
        raise HTTPException(404, f"Need {need_id} not found")

    payment_sig = request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
    if payment_sig:
        receipt = Receipt(
            type=ReceiptType.payment,
            need_id=need.id,
            project_id=need.project_id,
            from_entity="x402-payer",
            to_entity=need.pay_to[0].address if need.pay_to else "unknown",
            amount=need.amount_or_bounty.target,
            tx_hash=payment_sig[:66] if len(payment_sig) > 10 else payment_sig,
            provenance=Provenance(source="needrail.x402", attested_by="x402"),
        )
        reg.add_receipt(receipt)
        if need.status == NeedStatus.open:
            need.status = NeedStatus.funded
            reg.update_need(need)
        return {
            "status": "funded",
            "need_id": need.id,
            "receipt_id": receipt.id,
            "message": "Payment accepted and receipt recorded",
        }

    accepts = []
    for w in need.pay_to:
        accepts.append(
            {
                "scheme": "exact",
                "network": w.chain,
                "maxAmountRequired": need.amount_or_bounty.target,
                "asset": getattr(w, "asset", None) or need.amount_or_bounty.asset,
                "payTo": w.address,
                "resource": f"/needs/{need_id}/fund",
                "description": f"Fund Need: {need.title}",
            }
        )

    body = {
        "x402Version": 1,
        "error": "Payment Required",
        "accepts": accepts,
        "need_id": need.id,
        "title": need.title,
    }
    return JSONResponse(status_code=402, content=body, headers={"PAYMENT-REQUIRED": "true"})


@app.post("/needs/{need_id}/claim")
def claim_need(need_id: str, claimer: str):
    from .adapters.erc8004 import resolve_requester
    from .adapters.antispam import get_deposit_ledger, DepositKind, DEFAULT_CLAIM_DEPOSIT

    reg = get_registry()
    identity = resolve_requester(claimer)
    ref = identity.get("ref") or claimer
    try:
        need = reg.claim_need(need_id, ref)
    except (KeyError, ValueError) as e:
        raise HTTPException(400, str(e))
    dep = get_deposit_ledger().lock(DepositKind.claim, need_id, ref, DEFAULT_CLAIM_DEPOSIT)
    out = need.model_dump(mode="json", by_alias=True)
    out["identity"] = identity
    out["claim_deposit"] = dep.model_dump(mode="json")
    return out


@app.post("/needs/{need_id}/complete")
def complete_need(need_id: str, completer: str, evidence_links: list[str]):
    reg = get_registry()
    try:
        need = reg.complete_need(need_id, evidence_links, completer)
        return need.model_dump(mode="json", by_alias=True)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.get("/receipts")
def get_receipts(need_id: Optional[str] = None, project_id: Optional[str] = None):
    reg = get_registry()
    return [
        r.model_dump(mode="json", by_alias=True)
        for r in reg.get_receipts(need_id=need_id, project_id=project_id)
    ]


@app.get("/agents/{agent_ref}/reputation")
def agent_reputation(agent_ref: str):
    from urllib.parse import unquote
    from .reputation import reputation_for

    return reputation_for(unquote(agent_ref), get_registry())


@app.get("/production")
def production_status():
    """Honest production readiness surface."""
    import os
    from .adapters.eas import registration_instructions
    from .adapters.erc8183_onchain import get_onchain_config

    eas = registration_instructions()
    esc = get_onchain_config()
    return {
        "non_custodial_default": True,
        "erc8004_live_lookup": True,
        "eas_schemas_registered": eas.get("registered"),
        "eas_registration_steps": eas.get("steps"),
        "erc8183_onchain_enabled": esc.use_onchain,
        "erc8183_contract": esc.contract,
        "facilitator": os.getenv("NEEDRAIL_FACILITATOR_URL", "https://x402.org/facilitator"),
        "client": "client/index.html",
        "next_human_steps": [
            "Register EAS schemas on base.easscan.org; set NEEDRAIL_EAS_RECEIPT_SCHEMA and NEEDRAIL_EAS_COMPLETION_SCHEMA",
            "Publish MCP server to the official MCP Registry",
            "List funding URL on Agentic.market / x402 Bazaar",
            "Set NEEDRAIL_FACILITATOR_URL to a production facilitator",
        ],
    }


def main():
    import uvicorn

    uvicorn.run("needrail.server:app", host="0.0.0.0", port=8420, reload=False)


if __name__ == "__main__":
    main()
