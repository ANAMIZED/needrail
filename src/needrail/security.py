"""NeedRail security primitives — prompt-injection hardening & spending policy.

All free-text fields (Need description, evidence) are treated as untrusted.
Paying decisions must never be driven solely by free-text content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SpendingPolicy:
    """Hard limits for any agent that can move value."""
    max_per_tx: str = "10"          # USDC (decimal string)
    max_daily: str = "100"
    max_per_need: str = "50"
    allowed_networks: list[str] = field(default_factory=lambda: ["eip155:8453"])
    allowed_assets: list[str] = field(default_factory=lambda: ["USDC"])
    require_attestation_for_amounts_above: str = "25"
    block_free_text_driven_payment: bool = True


DEFAULT_POLICY = SpendingPolicy()


def is_amount_within_policy(amount: str, policy: SpendingPolicy = DEFAULT_POLICY) -> bool:
    try:
        return float(amount) <= float(policy.max_per_tx)
    except ValueError:
        return False


def sanitize_for_agent(text: str, max_len: int = 4000) -> str:
    """
    Basic hygiene for free-text that will be shown to an agent.
    Does not claim to be a complete prompt-injection defense.
    Callers must still apply spending policies and never let free text
    alone authorize a transfer.
    """
    if not text:
        return ""
    cleaned = text.replace("\x00", "")[:max_len]
    return cleaned


def payment_allowed(
    amount: str,
    network: str,
    asset: str,
    policy: SpendingPolicy = DEFAULT_POLICY,
    has_independent_attestation: bool = False,
) -> tuple[bool, str]:
    """
    Pre-execution gate. Returns (allowed, reason).
    """
    if network not in policy.allowed_networks:
        return False, f"network {network} not in allow-list"
    if asset not in policy.allowed_assets:
        return False, f"asset {asset} not in allow-list"
    try:
        amt = float(amount)
    except ValueError:
        return False, "invalid amount"
    if amt > float(policy.max_per_tx):
        return False, f"amount {amount} exceeds max_per_tx {policy.max_per_tx}"
    if amt > float(policy.require_attestation_for_amounts_above) and not has_independent_attestation:
        return False, "amount requires independent attestation"
    return True, "ok"
