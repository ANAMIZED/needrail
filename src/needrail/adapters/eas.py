"""Map NeedRail Receipts to Ethereum Attestation Service (EAS) schemas."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

NEEDRAIL_RECEIPT_SCHEMA_UID = "0x0000000000000000000000000000000000000000000000000000000000000000"
NEEDRAIL_COMPLETION_SCHEMA_UID = "0x0000000000000000000000000000000000000000000000000000000000000001"


class EASAttestationPayload(BaseModel):
    schema_uid: str
    recipient: str
    expiration_time: int = 0
    revocable: bool = True
    ref_uid: str = "0x" + "00" * 32
    data: dict[str, Any]
    value: int = 0


def receipt_to_eas_payload(
    receipt: dict[str, Any],
    schema_uid: str = NEEDRAIL_RECEIPT_SCHEMA_UID,
) -> EASAttestationPayload:
    return EASAttestationPayload(
        schema_uid=schema_uid,
        recipient=receipt.get("to") or receipt.get("to_entity") or "0x0000000000000000000000000000000000000000",
        data={
            "type": receipt.get("type"),
            "need_id": receipt.get("need_id"),
            "project_id": receipt.get("project_id"),
            "from": receipt.get("from") or receipt.get("from_entity"),
            "to": receipt.get("to") or receipt.get("to_entity"),
            "amount": receipt.get("amount"),
            "tx_hash": receipt.get("tx_hash"),
            "evidence": receipt.get("evidence") or [],
            "timestamp": str(receipt.get("timestamp")),
            "provenance_source": (receipt.get("provenance") or {}).get("source"),
            "content_hash": (receipt.get("provenance") or {}).get("content_hash"),
        },
    )


def completion_to_eas_payload(
    need_id: str,
    completer: str,
    evidence: list[str],
    recipient: str,
    schema_uid: str = NEEDRAIL_COMPLETION_SCHEMA_UID,
) -> EASAttestationPayload:
    return EASAttestationPayload(
        schema_uid=schema_uid,
        recipient=recipient,
        data={
            "need_id": need_id,
            "completer": completer,
            "evidence": evidence,
            "attestation_type": "completion",
        },
    )


def eas_uid_from_receipt(receipt_id: str) -> str:
    return f"eas:needrail:{receipt_id}"
