"""NeedRail core data models — provenance first, agent-native."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class NeedType(str, Enum):
    bug = "bug"
    feature = "feature"
    docs = "docs"
    security = "security"
    runway = "runway"
    data = "data"
    compute = "compute"
    other = "other"


class NeedStatus(str, Enum):
    open = "open"
    funded = "funded"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Provenance(BaseModel):
    source: str
    timestamp: datetime = Field(default_factory=utcnow)
    attested_by: Optional[str] = None
    content_hash: Optional[str] = None


class Wallet(BaseModel):
    chain: str  # e.g. "eip155:8453"
    address: str
    asset: str = "USDC"


class Amount(BaseModel):
    target: str  # decimal string
    asset: str = "USDC"
    network: str = "eip155:8453"
    partial_ok: bool = True


class Project(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    description: str = ""
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: str = "Apache-2.0"
    maintainers: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    funding_wallets: list[Wallet] = Field(default_factory=list)
    provenance: Provenance
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Need(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: Optional[str] = None
    requester: str  # agent-id | wallet | did
    type: NeedType = NeedType.other
    title: str
    description: str = ""
    amount_or_bounty: Amount
    acceptance_criteria: list[str] = Field(default_factory=list)
    pay_to: list[Wallet] = Field(default_factory=list)
    status: NeedStatus = NeedStatus.open
    evidence_links: list[str] = Field(default_factory=list)
    claimed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    provenance: Provenance
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ReceiptType(str, Enum):
    payment = "payment"
    delivery = "delivery"
    completion = "completion"


class Receipt(BaseModel):
    id: str = Field(default_factory=new_id)
    type: ReceiptType
    need_id: Optional[str] = None
    project_id: Optional[str] = None
    from_entity: str = Field(alias="from")
    to_entity: str = Field(alias="to")
    amount: Optional[str] = None
    tx_hash: Optional[str] = None
    evidence: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utcnow)
    signature: Optional[str] = None
    provenance: Provenance

    class Config:
        populate_by_name = True


class CreateNeedRequest(BaseModel):
    project_id: Optional[str] = None
    requester: str
    type: NeedType = NeedType.other
    title: str
    description: str = ""
    amount_or_bounty: Amount
    acceptance_criteria: list[str] = Field(default_factory=list)
    pay_to: list[Wallet] = Field(default_factory=list)
    evidence_links: list[str] = Field(default_factory=list)
    provenance_source: str = "agent"


class FundNeedResponse(BaseModel):
    need_id: str
    payment_required: bool = True
    accepts: list[dict[str, Any]]
    description: str
    pay_to: list[Wallet]
    amount: Amount
