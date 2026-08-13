"""Adapters for external standards — compose, don't reinvent."""

from .erc8004 import bind_requester, lookup_agent, ERC8004Identity
from .erc8183 import get_escrow_adapter, EscrowJob, JobState
from .eas import receipt_to_eas_payload, completion_to_eas_payload, eas_uid_from_receipt
from .antispam import get_deposit_ledger, DepositKind, DepositStatus, DEFAULT_CREATE_DEPOSIT, DEFAULT_CLAIM_DEPOSIT

__all__ = [
    "bind_requester",
    "lookup_agent",
    "ERC8004Identity",
    "get_escrow_adapter",
    "EscrowJob",
    "JobState",
    "receipt_to_eas_payload",
    "completion_to_eas_payload",
    "eas_uid_from_receipt",
    "get_deposit_ledger",
    "DepositKind",
    "DepositStatus",
    "DEFAULT_CREATE_DEPOSIT",
    "DEFAULT_CLAIM_DEPOSIT",
]
