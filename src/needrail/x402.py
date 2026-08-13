"""NeedRail x402 integration — payment is the authentication.

Supports any compliant facilitator. Prefer open / non-custodial ones.
Default public facilitators can be overridden via NEEDRAIL_FACILITATOR_URL.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

# Open / permissionless facilitators (examples — agents can point to any)
DEFAULT_FACILITATORS = [
    "https://x402.org/facilitator",          # reference
    "https://facilitator.openx402.ai",      # permissionless
    "https://pay.openfacilitator.io",       # open source
]

FACILITATOR_URL = os.getenv("NEEDRAIL_FACILITATOR_URL", DEFAULT_FACILITATORS[0])


async def verify_payment(
    payload: dict[str, Any],
    facilitator_url: Optional[str] = None,
) -> dict[str, Any]:
    """
    Call facilitator /verify endpoint.
    Returns verification result. Does not settle.
    """
    url = (facilitator_url or FACILITATOR_URL).rstrip("/") + "/verify"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def settle_payment(
    payload: dict[str, Any],
    facilitator_url: Optional[str] = None,
) -> dict[str, Any]:
    """
    Call facilitator /settle endpoint.
    Returns settlement result (tx hash etc.).
    """
    url = (facilitator_url or FACILITATOR_URL).rstrip("/") + "/settle"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def build_payment_requirements(
    pay_to: str,
    amount: str,
    network: str = "eip155:8453",
    asset: str = "USDC",
    resource: str = "",
    description: str = "",
) -> dict[str, Any]:
    """Build a standard x402 PaymentRequirements object."""
    return {
        "x402Version": 1,
        "error": "Payment Required",
        "accepts": [
            {
                "scheme": "exact",
                "network": network,
                "maxAmountRequired": amount,
                "asset": asset,
                "payTo": pay_to,
                "resource": resource,
                "description": description,
            }
        ],
    }


def is_payment_present(headers: dict[str, str]) -> bool:
    """Check common x402 payment proof headers."""
    return bool(
        headers.get("payment-signature")
        or headers.get("PAYMENT-SIGNATURE")
        or headers.get("x-payment")
        or headers.get("X-PAYMENT")
    )


def extract_payment_payload(headers: dict[str, str]) -> Optional[str]:
    return (
        headers.get("payment-signature")
        or headers.get("PAYMENT-SIGNATURE")
        or headers.get("x-payment")
        or headers.get("X-PAYMENT")
    )
