"""ERC-8004 identity binding — registration & lookup helpers.

ERC-8004 is live but empirically weak on reputation (high Sybil rates).
NeedRail uses it as *identity*, not as a finished trust signal.
Compose with cost-to-create or stake when registering new agents.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

IDENTITY_REGISTRIES: dict[str, str] = {
    "eip155:1": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:8453": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:56": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "eip155:137": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
}

REPUTATION_REGISTRIES: dict[str, str] = {
    "eip155:1": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    "eip155:8453": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
    "eip155:56": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
}


class ERC8004Identity(BaseModel):
    agent_id: int
    owner: str
    metadata_uri: Optional[str] = None
    chain: str = "eip155:8453"
    registry: Optional[str] = None
    endpoints: list[str] = Field(default_factory=list)
    payment_address: Optional[str] = None
    raw: dict[str, Any] = Field(default_factory=dict)


def registry_for(chain: str = "eip155:8453") -> Optional[str]:
    return IDENTITY_REGISTRIES.get(chain)


def parse_agent_ref(ref: str) -> tuple[str, Optional[int]]:
    """
    Accept forms:
      - "erc8004:12345"
      - "erc8004:8453:12345"
      - "erc8004:eip155:8453:12345"
      - plain number string
      - wallet / DID (returned as-is, agent_id=None)
    """
    if ref.startswith("erc8004:"):
        parts = ref.split(":")
        if len(parts) == 2:
            return "eip155:8453", int(parts[1])
        if len(parts) == 3:
            return f"eip155:{parts[1]}", int(parts[2])
        if len(parts) >= 4:
            chain = f"{parts[1]}:{parts[2]}"
            return chain, int(parts[-1])
    try:
        return "eip155:8453", int(ref)
    except ValueError:
        return ref, None


async def lookup_agent(
    agent_id: int,
    chain: str = "eip155:8453",
    rpc_url: Optional[str] = None,
) -> Optional[ERC8004Identity]:
    """
    Lookup an ERC-8004 agent identity.
    Production: call the Identity Registry + resolve metadata URI.
    """
    registry = registry_for(chain)
    if not registry:
        return None
    return ERC8004Identity(
        agent_id=agent_id,
        owner="0x0000000000000000000000000000000000000000",
        metadata_uri=None,
        chain=chain,
        registry=registry,
        endpoints=[],
        payment_address=None,
        raw={"note": "stub — wire live RPC + tokenURI resolution in production"},
    )


def bind_requester(requester: str) -> dict[str, Any]:
    """Normalize a requester string into identity metadata for Need creation."""
    chain, agent_id = parse_agent_ref(requester)
    if agent_id is not None:
        return {
            "scheme": "erc8004",
            "value": str(agent_id),
            "chain": chain,
            "ref": f"erc8004:{chain}:{agent_id}" if chain.startswith("eip155:") else f"erc8004:{agent_id}",
        }
    if requester.startswith("did:"):
        return {"scheme": "did", "value": requester, "ref": requester}
    if requester.startswith("0x") and len(requester) == 42:
        return {"scheme": "wallet", "value": requester, "ref": requester}
    return {"scheme": "opaque", "value": requester, "ref": requester}
