# NeedRail Status — Live Agent-Commerce Public Good

**Code complete.** Audit: 58/58. Repo: https://github.com/ANAMIZED/needrail

## Live surfaces

| Surface | Path |
|---------|------|
| HTTP + x402 402 | `uvicorn needrail.server:app --port 8420` |
| MCP | `python -m needrail.mcp_server` |
| Production status | `GET /production` |
| Reputation | `GET /agents/{ref}/reputation` |
| Client | `client/app.full.html` (clone) / `client/index.html` |
| Seed from client | `python scripts/seed_from_client.py export.json` |

## Invariants (enforced)

- Non-custodial default (direct-to-`pay_to`)
- ERC-8004 live lookup on create/claim
- Anti-spam deposits on create/claim
- Free-text sanitized; spending policy gates
- Optional ERC-8183 escrow (opt-in)
- EAS-mappable receipts

## Operator one-time (wallet / registry accounts)

1. Register EAS schemas → `NEEDRAIL_EAS_*`
2. `NEEDRAIL_FACILITATOR_URL` → production facilitator
3. Publish to Agentic.market + MCP Registry
4. Host node behind TLS

See [GO_LIVE.md](./GO_LIVE.md).
