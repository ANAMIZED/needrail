"""ERC-8004 identity binding — live RPC lookup.

Identity Registry (CREATE2): 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
Verified live against Base mainnet (agent 2106 resolves).
"""

from __future__ import annotations

import os
from typing import Any, Optional

from pydantic import BaseModel, Field

from .rpc import call_owner_of, call_token_uri, rpc_url

IDENTITY_REGISTRIES = {
    "eip155:1": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:8453": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:56": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:137": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
}

REPUTATION_REGISTRIES = {
    "eip155:1": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    "eip155:8453": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    "eip155:56": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
}

FORCE_STUB = os.getenv("NEEDRAIL_ERC8004_STUB", "").lower() in ("1", "true", "yes")


class ERC8004Identity(BaseModel):
    agent_id: int
    owner: str
    metadata_uri: Optional[str] = None
    chain: str = "eip155:8453"
    registry: Optional[str] = None
    endpoints: list[str] = Field(default_factory=list)
    payment_address: Optional[str] = None
    live: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


def registry_for(chain: str = "eip155:8453") -> Optional[str]:
    return IDENTITY_REGISTRIES.get(chain)


def parse_agent_ref(ref: str):
    if ref.startswith("erc8004:"):
        parts = ref.split(":")
        if len(parts) == 2:
            return "eip155:8453", int(parts[1])
        if len(parts) == 3:
            return f"eip155:{parts[1]}", int(parts[2])
        if len(parts) >= 4:
            return f"{parts[1]}:{parts[2]}", int(parts[-1])
    try:
        return "eip155:8453", int(ref)
    except ValueError:
        return ref, None


def lookup_agent_sync(agent_id: int, chain: str = "eip155:8453") -> Optional[ERC8004Identity]:
    registry = registry_for(chain)
    if not registry:
        return None
    if FORCE_STUB:
        return ERC8004Identity(
            agent_id=agent_id, owner="0x0000000000000000000000000000000000000000",
            chain=chain, registry=registry, live=False, raw={"note": "FORCE_STUB"},
        )
    try:
        owner = call_owner_of(registry, agent_id, chain=chain)
        if owner.lower() == "0x0000000000000000000000000000000000000000":
            return None
        uri = ""
        try:
            uri = call_token_uri(registry, agent_id, chain=chain)
        except Exception:
            uri = ""
        return ERC8004Identity(
            agent_id=agent_id, owner=owner, metadata_uri=uri or None,
            chain=chain, registry=registry, live=True, raw={"rpc": rpc_url(chain)},
        )
    except Exception as e:
        return ERC8004Identity(
            agent_id=agent_id, owner="0x0000000000000000000000000000000000000000",
            chain=chain, registry=registry, live=False,
            raw={"error": str(e), "note": "RPC unavailable — stub returned"},
        )


async def lookup_agent(agent_id: int, chain: str = "eip155:8453", rpc_url: Optional[str] = None):
    return lookup_agent_sync(agent_id, chain=chain)


def bind_requester(requester: str) -> dict[str, Any]:
    chain, agent_id = parse_agent_ref(requester)
    if agent_id is not None:
        return {"scheme": "erc8004", "value": str(agent_id), "chain": chain, "ref": f"erc8004:{chain}:{agent_id}"}
    if requester.startswith("did:"):
        return {"scheme": "did", "value": requester, "ref": requester}
    if requester.startswith("0x") and len(requester) == 42:
        return {"scheme": "wallet", "value": requester, "ref": requester}
    return {"scheme": "opaque", "value": requester, "ref": requester}


def resolve_requester(requester: str) -> dict[str, Any]:
    meta = bind_requester(requester)
    if meta["scheme"] == "erc8004":
        ident = lookup_agent_sync(int(meta["value"]), chain=meta.get("chain", "eip155:8453"))
        if ident:
            meta["owner"] = ident.owner
            meta["metadata_uri"] = ident.metadata_uri
            meta["live"] = ident.live
    return meta
