"""Map NeedRail Receipts to Ethereum Attestation Service (EAS).

Base mainnet:
  Schema Registry: 0x4200000000000000000000000000000000000020
  EAS:             0x4200000000000000000000000000000000000021

Set NEEDRAIL_EAS_RECEIPT_SCHEMA / NEEDRAIL_EAS_COMPLETION_SCHEMA after registration.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from pydantic import BaseModel

EAS_CONTRACTS = {
    "eip155:8453": {
        "schema_registry": "0x4200000000000000000000000000000000000020",
        "eas": "0x4200000000000000000000000000000000000021",
    },
}

NEEDRAIL_RECEIPT_SCHEMA_DEF = (
    "string type,string need_id,string project_id,string fromEntity,"
    "string toEntity,string amount,string tx_hash,string[] evidence,"
    "string timestamp,string provenance_source,string content_hash"
)
NEEDRAIL_COMPLETION_SCHEMA_DEF = (
    "string need_id,string completer,string[] evidence,string attestation_type"
)

NEEDRAIL_RECEIPT_SCHEMA_UID = os.getenv(
    "NEEDRAIL_EAS_RECEIPT_SCHEMA",
    "0x0000000000000000000000000000000000000000000000000000000000000000",
)
NEEDRAIL_COMPLETION_SCHEMA_UID = os.getenv(
    "NEEDRAIL_EAS_COMPLETION_SCHEMA",
    "0x0000000000000000000000000000000000000000000000000000000000000001",
)


class EASAttestationPayload(BaseModel):
    schema_uid: str
    recipient: str
    expiration_time: int = 0
    revocable: bool = True
    ref_uid: str = "0x" + "00" * 32
    data: dict[str, Any]
    value: int = 0
    schema_def: Optional[str] = None
    chain: str = "eip155:8453"
    eas_contract: Optional[str] = None
    schema_registry: Optional[str] = None


def contracts_for(chain: str = "eip155:8453"):
    return EAS_CONTRACTS.get(chain, EAS_CONTRACTS["eip155:8453"])


def receipt_to_eas_payload(receipt: dict[str, Any], schema_uid: Optional[str] = None, chain: str = "eip155:8453"):
    c = contracts_for(chain)
    return EASAttestationPayload(
        schema_uid=schema_uid or NEEDRAIL_RECEIPT_SCHEMA_UID,
        recipient=receipt.get("to") or receipt.get("to_entity") or "0x0000000000000000000000000000000000000000",
        data={
            "type": receipt.get("type"),
            "need_id": receipt.get("need_id"),
            "project_id": receipt.get("project_id"),
            "fromEntity": receipt.get("from") or receipt.get("from_entity"),
            "toEntity": receipt.get("to") or receipt.get("to_entity"),
            "amount": receipt.get("amount"),
            "tx_hash": receipt.get("tx_hash"),
            "evidence": receipt.get("evidence") or [],
            "timestamp": str(receipt.get("timestamp")),
            "provenance_source": (receipt.get("provenance") or {}).get("source"),
            "content_hash": (receipt.get("provenance") or {}).get("content_hash"),
        },
        schema_def=NEEDRAIL_RECEIPT_SCHEMA_DEF,
        chain=chain,
        eas_contract=c["eas"],
        schema_registry=c["schema_registry"],
    )


def completion_to_eas_payload(need_id: str, completer: str, evidence: list, recipient: str, schema_uid: Optional[str] = None, chain: str = "eip155:8453"):
    c = contracts_for(chain)
    return EASAttestationPayload(
        schema_uid=schema_uid or NEEDRAIL_COMPLETION_SCHEMA_UID,
        recipient=recipient,
        data={"need_id": need_id, "completer": completer, "evidence": evidence, "attestation_type": "completion"},
        schema_def=NEEDRAIL_COMPLETION_SCHEMA_DEF,
        chain=chain,
        eas_contract=c["eas"],
        schema_registry=c["schema_registry"],
    )


def eas_uid_from_receipt(receipt_id: str) -> str:
    return f"eas:needrail:{receipt_id}"


def registration_instructions() -> dict:
    return {
        "base_schema_registry": EAS_CONTRACTS["eip155:8453"]["schema_registry"],
        "base_eas": EAS_CONTRACTS["eip155:8453"]["eas"],
        "receipt_schema": NEEDRAIL_RECEIPT_SCHEMA_DEF,
        "completion_schema": NEEDRAIL_COMPLETION_SCHEMA_DEF,
        "steps": [
            "1. https://base.easscan.org/schema/create",
            "2. Register receipt schema; set NEEDRAIL_EAS_RECEIPT_SCHEMA",
            "3. Register completion schema; set NEEDRAIL_EAS_COMPLETION_SCHEMA",
        ],
        "current_receipt_uid": NEEDRAIL_RECEIPT_SCHEMA_UID,
        "registered": not NEEDRAIL_RECEIPT_SCHEMA_UID.endswith("0000"),
    }
