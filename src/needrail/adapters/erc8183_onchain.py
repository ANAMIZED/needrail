"""Production ERC-8183 on-chain adapter configuration.

Default NeedRail path remains non-custodial direct-to-pay_to.
Escrow is opt-in via NEEDRAIL_ERC8183_ONCHAIN=1.
NeedRail never holds funds or private keys.
"""

from __future__ import annotations

import os
import time
from typing import Any

from pydantic import BaseModel, Field

ERC8183_CONTRACTS = {
    "eip155:8453": {
        "default": os.getenv(
            "NEEDRAIL_ERC8183_BASE",
            "0x16213AB6a660A24f36d4F8DdACA7a3d0856A8AF5",  # Clawplaza ACPCore Base
        ),
        "ufx": "0x1b32B85c914ea30E81F08550c1EBFC5b9d32a855",
    },
}


class OnChainEscrowConfig(BaseModel):
    chain: str = "eip155:8453"
    contract: str = Field(
        default_factory=lambda: ERC8183_CONTRACTS["eip155:8453"]["default"]
    )
    payment_token: str = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC Base
    use_onchain: bool = False


def get_onchain_config(chain: str = "eip155:8453") -> OnChainEscrowConfig:
    use = os.getenv("NEEDRAIL_ERC8183_ONCHAIN", "").lower() in ("1", "true", "yes")
    contract = os.getenv("NEEDRAIL_ERC8183_CONTRACT") or ERC8183_CONTRACTS.get(chain, {}).get("default", "")
    return OnChainEscrowConfig(chain=chain, contract=contract, use_onchain=use)


def onchain_job_params(
    need_id: str,
    client: str,
    provider: str,
    evaluator: str,
    amount: str,
    description: str = "",
    timeout_seconds: int = 7 * 24 * 3600,
    chain: str = "eip155:8453",
) -> dict[str, Any]:
    """Build params for a live ERC-8183 createJob. Caller signs/submits."""
    cfg = get_onchain_config(chain)
    return {
        "contract": cfg.contract,
        "chain": chain,
        "payment_token": cfg.payment_token,
        "client": client,
        "provider": provider,
        "evaluator": evaluator,
        "amount": amount,
        "description": description or f"NeedRail Need {need_id}",
        "expired_at": int(time.time()) + timeout_seconds,
        "hook": "0x0000000000000000000000000000000000000000",
        "need_id": need_id,
        "note": "Submit via ERC-8183 SDK/wallet — NeedRail remains non-custodial",
    }
