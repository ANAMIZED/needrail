# NeedRail Client

Interactive **registry + human UI** for the Need object.

## Open the client

```bash
open client/app.full.html   # full single-file UI (recommended)
# index.html redirects here when both are present
```

## Client vs Node

| | **Client** | **Node** (Python) |
|--|------------|-------------------|
| Role | Local registry, signed receipts, human UI, wallet links | MCP tools, HTTP 402 / x402, ERC-8004 / EAS / ERC-8183 |
| Identity | Device `did:key` (WebCrypto) | ERC-8004 live lookup |
| Payments | Direct-to-`pay_to` (EIP-681 / Solana Pay + QR) | Machine-native 402 + facilitator |
| MCP / x402 server | **No** | **Yes** |

## Export → seed the node

1. Client: **Agent → Export JSON** → `needrail-registry.json` (private key excluded)
2. Seed:

```bash
python scripts/seed_from_client.py needrail-registry.json
```

3. Optional: **Agent → Settings → NeedRail node URL** (e.g. `http://127.0.0.1:8000`)  
   Fund sheets then offer **Open 402 on node** → `{node}/needs/{id}/fund`

## What this is not

- Not an MCP server  
- Not an x402 402 endpoint  
- Not multi-node federation  

Those live in the Python node. The About panel already states this correctly.

## Design invariants

- Non-custodial — page never holds funds  
- Payments final; receipts signed and verifiable  
- Reputation = completed count + value only  
