# NeedRail Production Wiring

## Default path remains non-custodial

`pay_to` direct settlement is the default. Escrow is **opt-in**.
NeedRail never takes custody of funds.

## ERC-8004 live lookup

```python
from needrail.adapters import lookup_agent_sync, resolve_requester

ident = lookup_agent_sync(2106, "eip155:8453")
# live=True, owner=0xd386…, metadata_uri=ipfs://…

meta = resolve_requester("erc8004:8453:2106")
```

- Registry (CREATE2): `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- RPC: `NEEDRAIL_RPC_BASE` (default `https://mainnet.base.org`) or `NEEDRAIL_RPC_URL`
- Verified live against Base mainnet (agent 2106 resolves)

## EAS schemas

Base contracts:
- Schema Registry: `0x4200…0020`
- EAS: `0x4200…0021`

Register once:

```bash
# See registration_instructions()
# 1. https://base.easscan.org/schema/create
# 2. Receipt schema string is in NEEDRAIL_RECEIPT_SCHEMA_DEF
# 3. Set env:
export NEEDRAIL_EAS_RECEIPT_SCHEMA=0x<uid>
export NEEDRAIL_EAS_COMPLETION_SCHEMA=0x<uid>
```

Until registered, local refs `eas:needrail:<receipt_id>` are used.

## ERC-8183 optional escrow

In-process state machine: always available (`get_escrow_adapter()`).

On-chain (opt-in):

```bash
export NEEDRAIL_ERC8183_ONCHAIN=1
export NEEDRAIL_ERC8183_CONTRACT=0x16213AB6a660A24f36d4F8DdACA7a3d0856A8AF5  # Base reference
```

```python
from needrail.adapters import onchain_job_params, get_onchain_config
params = onchain_job_params(need_id, client, provider, evaluator, amount)
# Submit via wallet/SDK — NeedRail does not hold keys or funds
```

## Env reference

| Variable | Purpose |
|----------|--------|
| `NEEDRAIL_RPC_URL` / `NEEDRAIL_RPC_BASE` | JSON-RPC endpoint |
| `NEEDRAIL_ERC8004_STUB=1` | Force offline identity stub |
| `NEEDRAIL_EAS_RECEIPT_SCHEMA` | On-chain EAS schema UID |
| `NEEDRAIL_EAS_COMPLETION_SCHEMA` | On-chain EAS schema UID |
| `NEEDRAIL_ERC8183_ONCHAIN=1` | Enable on-chain escrow params |
| `NEEDRAIL_ERC8183_CONTRACT` | Override ERC-8183 contract |
| `NEEDRAIL_FACILITATOR_URL` | x402 facilitator |
