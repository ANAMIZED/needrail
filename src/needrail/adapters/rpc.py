"""Minimal JSON-RPC helpers for production on-chain reads (no heavy deps)."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

DEFAULT_RPC: dict[str, str] = {
    "eip155:1": os.getenv("NEEDRAIL_RPC_ETHEREUM", "https://eth.llamarpc.com"),
    "eip155:8453": os.getenv("NEEDRAIL_RPC_BASE", "https://mainnet.base.org"),
    "eip155:56": os.getenv("NEEDRAIL_RPC_BNB", "https://bsc-dataseed.binance.org"),
    "eip155:137": os.getenv("NEEDRAIL_RPC_POLYGON", "https://polygon-rpc.com"),
}


def rpc_url(chain: str = "eip155:8453") -> str:
    return os.getenv("NEEDRAIL_RPC_URL") or DEFAULT_RPC.get(chain, DEFAULT_RPC["eip155:8453"])


def _encode_uint256(n: int) -> str:
    return hex(n)[2:].zfill(64)


def _selector(sig: str) -> str:
    KNOWN = {
        "ownerOf(uint256)": "6352211e",
        "tokenURI(uint256)": "c87b56dd",
        "balanceOf(address)": "70a08231",
    }
    if sig in KNOWN:
        return KNOWN[sig]
    raise ValueError(f"unknown selector for {sig}")


def eth_call(to: str, data: str, chain: str = "eip155:8453", block: str = "latest") -> str:
    url = rpc_url(chain)
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": data}, block]}
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "error" in body:
            raise RuntimeError(body["error"])
        return body.get("result") or "0x"


def decode_address(hexdata: str) -> str:
    h = hexdata[2:] if hexdata.startswith("0x") else hexdata
    if len(h) < 64:
        return "0x" + h.zfill(40)
    return "0x" + h[-40:]


def decode_string(hexdata: str) -> str:
    h = hexdata[2:] if hexdata.startswith("0x") else hexdata
    if len(h) < 128:
        return ""
    try:
        length = int(h[64:128], 16)
        data_hex = h[128 : 128 + length * 2]
        return bytes.fromhex(data_hex).decode("utf-8", errors="replace")
    except Exception:
        return ""


def call_owner_of(registry: str, agent_id: int, chain: str = "eip155:8453") -> str:
    data = "0x" + _selector("ownerOf(uint256)") + _encode_uint256(agent_id)
    return decode_address(eth_call(registry, data, chain=chain))


def call_token_uri(registry: str, agent_id: int, chain: str = "eip155:8453") -> str:
    data = "0x" + _selector("tokenURI(uint256)") + _encode_uint256(agent_id)
    return decode_string(eth_call(registry, data, chain=chain))
