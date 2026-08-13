# NeedRail Verification Report

**Date:** 2026-08-13  
**Suite:** `tests/test_needrail.py`  
**Result:** **58 passed, 0 failed**

## Coverage

| Area | Checks | Status |
|------|--------|--------|
| Models (Need, Receipt, Identity, Escrow, Attestation) | 5 | PASS |
| Content-addressed storage | 3 | PASS |
| Security / spending policy / sanitization | 7 | PASS |
| ERC-8004 identity parse & bind | 6 | PASS |
| ERC-8183 escrow state machine | 6 | PASS |
| EAS receipt mapping | 4 | PASS |
| Anti-spam deposits | 4 | PASS |
| x402 helpers | 4 | PASS |
| Registry lifecycle (create→claim→receipt→complete) | 6 | PASS |
| MCP tool surface (10 tools) | 2 | PASS |
| HTTP + real 402 Payment Required | 5 | PASS |
| End-to-end hardened path | 6 | PASS |

## Phase status

| Phase | Status |
|-------|--------|
| Phase 0 — Foundation | Shipped & verified |
| Phase 1 — Trust infrastructure | Shipped & verified |
| Phase 2 — Anti-spam deposits + evaluator path | Shipped & verified |
| Phase 3 — Federation / live on-chain schemas | Spec'd; adapters ready for live wiring |

## How to re-run

```bash
PYTHONPATH=src python tests/test_needrail.py
```

## Notes

- ERC-8004 `lookup_agent` is a typed stub until live RPC is configured.
- EAS schema UIDs are placeholders until schemas are registered on-chain.
- Escrow adapter implements the ERC-8183 state machine in-process; production should call live contracts.
- Default path remains non-custodial direct-to-`pay_to`.
