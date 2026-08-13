# NeedRail Client

Interactive, single-file **registry + human UI** for the Need object.

Open [`index.html`](./index.html) in a modern browser (or host it statically).

## Client vs Node

| | **Client** (`client/index.html`) | **Node** (Python package) |
|--|----------------------------------|---------------------------|
| Role | Local registry, signed receipts, human UI, wallet payment links | MCP tools, HTTP 402 / x402, ERC-8004 / EAS / ERC-8183 adapters |
| Identity | Device `did:key` (WebCrypto) | ERC-8004 lookup + bind on create/claim |
| Payments | Direct-to-`pay_to` (EIP-681 / Solana Pay + QR) | Machine-native 402 + facilitator settle |
| Storage | Browser / Claude storage | File registry + optional multi-node CAS |
| MCP / x402 server | **No** | **Yes** |

The client is the fastest way to *feel* the data model.  
The node is what agents and production settlement use.

## Export client → seed the Python registry

1. In the client: **Agent → Export JSON**  
   Produces `needrail-registry.json` (`spec: needrail/v1`). Private key is **not** included.

2. Seed the node:

```bash
python scripts/seed_from_client.py needrail-registry.json
```

3. Optional: set **Agent → Settings → NeedRail node URL** in the client  
   (e.g. `http://127.0.0.1:8000`). Fund sheets then offer **Open 402 on node**.

## What this file is not

- Not an MCP server  
- Not an x402 endpoint that returns HTTP 402  
- Not multi-node federation  

Those live in the Python node. The client’s About panel already states this.

## Design invariants (client)

- Non-custodial: page never holds funds  
- Payments final; receipts are signed and verifiable  
- Reputation = completed count + value only  
- Content-addressed objects with provenance  
