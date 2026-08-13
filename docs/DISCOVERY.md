# Publishing NeedRail into existing discovery surfaces

NeedRail does **not** try to become the discovery layer.
It publishes into the surfaces agents already use.

## x402 Bazaar / Agentic.market

- **Agentic.market** (Coinbase): public directory of x402-enabled services  
  https://agentic.market
- **x402 Bazaar**: catalog of payment-gated services discovered by facilitators

### How to publish a NeedRail funding endpoint

1. Expose `GET/POST /needs/{id}/fund` with a correct x402 402 response (`accepts` array).
2. Register the resource with a facilitator that feeds Bazaar (or the public catalog).
3. Optionally advertise via a Bazaar MCP server / listing monitor.

NeedRail’s `/needs/{id}/fund` already returns a standards-shaped 402 body.
Point a facilitator or listing tool at your node URL.

## Official MCP Registry

1. Package the MCP server (`needrail.mcp_server`).
2. Register under a verified namespace in the official MCP Registry.
3. Keep `AGENTS.md` and `SKILL.md` accurate so clients that discover via files still work.

## Recommended agent discovery path

```
Agent → MCP Registry / AGENTS.md
     → list_needs / get_need
     → fund_need → x402 402
     → settle via facilitator
     → record_payment / complete_need
```

Do not build a parallel global index until Phase 3 and only with explicit indexer incentives.
