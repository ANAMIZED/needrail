"""Optional ERC-8183-style job escrow adapter.

Default NeedRail path remains direct-to-pay_to (non-custodial).
For higher-value Needs, funders can opt into: Client funds → Provider submits → Evaluator attests → release or refund.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobState(str, Enum):
    open = "open"
    funded = "funded"
    submitted = "submitted"
    completed = "completed"
    rejected = "rejected"
    expired = "expired"
    refunded = "refunded"


class EscrowJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    need_id: str
    client: str
    provider: Optional[str] = None
    evaluator: str
    amount: str
    asset: str = "USDC"
    network: str = "eip155:8453"
    state: JobState = JobState.open
    deliverable_uri: Optional[str] = None
    attestation_reason: Optional[str] = None
    timeout_at: Optional[datetime] = None
    escrow_tx: Optional[str] = None
    release_tx: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class EscrowAdapter:
    def __init__(self) -> None:
        self._jobs: dict[str, EscrowJob] = {}

    def create_job(
        self,
        need_id: str,
        client: str,
        evaluator: str,
        amount: str,
        asset: str = "USDC",
        network: str = "eip155:8453",
        timeout_seconds: Optional[int] = 7 * 24 * 3600,
    ) -> EscrowJob:
        timeout_at = None
        if timeout_seconds:
            timeout_at = utcnow() + timedelta(seconds=timeout_seconds)
        job = EscrowJob(
            need_id=need_id,
            client=client,
            evaluator=evaluator,
            amount=amount,
            asset=asset,
            network=network,
            state=JobState.open,
            timeout_at=timeout_at,
        )
        self._jobs[job.id] = job
        return job

    def fund(self, job_id: str, escrow_tx: str) -> EscrowJob:
        job = self._require(job_id)
        if job.state != JobState.open:
            raise ValueError(f"job {job_id} not open")
        job.state = JobState.funded
        job.escrow_tx = escrow_tx
        job.updated_at = utcnow()
        return job

    def assign_provider(self, job_id: str, provider: str) -> EscrowJob:
        job = self._require(job_id)
        if job.state not in (JobState.open, JobState.funded):
            raise ValueError(f"job {job_id} not assignable")
        job.provider = provider
        job.updated_at = utcnow()
        return job

    def submit(self, job_id: str, provider: str, deliverable_uri: str) -> EscrowJob:
        job = self._require(job_id)
        if job.state != JobState.funded:
            raise ValueError(f"job {job_id} not funded")
        if job.provider and job.provider != provider:
            raise ValueError("provider mismatch")
        job.provider = provider
        job.deliverable_uri = deliverable_uri
        job.state = JobState.submitted
        job.updated_at = utcnow()
        return job

    def complete(self, job_id: str, evaluator: str, reason: Optional[str] = None, release_tx: Optional[str] = None) -> EscrowJob:
        job = self._require(job_id)
        if job.state != JobState.submitted:
            raise ValueError(f"job {job_id} not submitted")
        if job.evaluator != evaluator:
            raise ValueError("only designated evaluator may complete")
        job.state = JobState.completed
        job.attestation_reason = reason
        job.release_tx = release_tx
        job.updated_at = utcnow()
        return job

    def reject(self, job_id: str, evaluator: str, reason: Optional[str] = None) -> EscrowJob:
        job = self._require(job_id)
        if job.state not in (JobState.funded, JobState.submitted):
            raise ValueError(f"job {job_id} not rejectable")
        if job.evaluator != evaluator:
            raise ValueError("only designated evaluator may reject")
        job.state = JobState.rejected
        job.attestation_reason = reason
        job.updated_at = utcnow()
        return job

    def get(self, job_id: str) -> Optional[EscrowJob]:
        return self._jobs.get(job_id)

    def list_for_need(self, need_id: str) -> list[EscrowJob]:
        return [j for j in self._jobs.values() if j.need_id == need_id]

    def _require(self, job_id: str) -> EscrowJob:
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"job {job_id} not found")
        return job


_adapter: Optional[EscrowAdapter] = None


def get_escrow_adapter() -> EscrowAdapter:
    global _adapter
    if _adapter is None:
        _adapter = EscrowAdapter()
    return _adapter
