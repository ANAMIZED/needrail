"""Economic anti-spam deposits (Phase 2).

Refundable stake on create_need and claim_need reduces free Sybil spam.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DepositKind(str, Enum):
    create = "create"
    claim = "claim"


class DepositStatus(str, Enum):
    locked = "locked"
    refunded = "refunded"
    forfeited = "forfeited"


class Deposit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    kind: DepositKind
    need_id: str
    from_entity: str
    amount: str
    asset: str = "USDC"
    network: str = "eip155:8453"
    status: DepositStatus = DepositStatus.locked
    tx_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    resolved_at: Optional[datetime] = None


DEFAULT_CREATE_DEPOSIT = "0.5"
DEFAULT_CLAIM_DEPOSIT = "0.25"


class DepositLedger:
    def __init__(self) -> None:
        self._deposits: dict[str, Deposit] = {}

    def lock(
        self,
        kind: DepositKind,
        need_id: str,
        from_entity: str,
        amount: str,
        tx_hash: Optional[str] = None,
        asset: str = "USDC",
        network: str = "eip155:8453",
    ) -> Deposit:
        d = Deposit(
            kind=kind,
            need_id=need_id,
            from_entity=from_entity,
            amount=amount,
            asset=asset,
            network=network,
            tx_hash=tx_hash,
            status=DepositStatus.locked,
        )
        self._deposits[d.id] = d
        return d

    def refund(self, deposit_id: str) -> Deposit:
        d = self._require(deposit_id)
        if d.status != DepositStatus.locked:
            raise ValueError("deposit not locked")
        d.status = DepositStatus.refunded
        d.resolved_at = utcnow()
        return d

    def forfeit(self, deposit_id: str) -> Deposit:
        d = self._require(deposit_id)
        if d.status != DepositStatus.locked:
            raise ValueError("deposit not locked")
        d.status = DepositStatus.forfeited
        d.resolved_at = utcnow()
        return d

    def for_need(self, need_id: str) -> list[Deposit]:
        return [d for d in self._deposits.values() if d.need_id == need_id]

    def _require(self, deposit_id: str) -> Deposit:
        d = self._deposits.get(deposit_id)
        if not d:
            raise KeyError(f"deposit {deposit_id} not found")
        return d


_ledger: Optional[DepositLedger] = None


def get_deposit_ledger() -> DepositLedger:
    global _ledger
    if _ledger is None:
        _ledger = DepositLedger()
    return _ledger
