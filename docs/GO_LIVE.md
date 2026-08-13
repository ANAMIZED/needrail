# NeedRail — Go Live Checklist

## Shipped in-repo

- MCP Need lifecycle · HTTP 402 · ERC-8004 live lookup · spending policy
- Optional ERC-8183 · EAS mapping · anti-spam deposits · reputation surface
- Human client · export→seed · CI · `.env.example`

## Operator one-time (keys/gas)

1. Register EAS schemas on base.easscan.org → set `NEEDRAIL_EAS_*`
2. Set `NEEDRAIL_FACILITATOR_URL` to a production facilitator
3. Publish to Agentic.market / x402 Bazaar + MCP Registry
4. Optional: `NEEDRAIL_ERC8183_ONCHAIN=1` (wallet/SDK submits; NeedRail holds no keys)
5. Host: `uvicorn needrail.server:app --host 0.0.0.0 --port 8420` behind TLS

## Verify

```bash
PYTHONPATH=src python tests/test_needrail.py
curl -s localhost:8420/production
curl -s -o /dev/null -w "%{http_code}" localhost:8420/needs/<id>/fund  # 402
```

Non-custodial by default · Provenance mandatory · Protocol over platform
