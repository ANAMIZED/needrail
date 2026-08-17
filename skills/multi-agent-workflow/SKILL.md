---
name: multi-agent-workflow
description: NeedRail multi-agent coordination — expressor → matcher → fulfiller under x402.
---

# Multi-agent workflow (NeedRail)

## Agents
- **expressor** — publish a need
- **matcher** — match providers / public goods
- **fulfiller** — coordinate settlement (x402 / attestations)

## Entry points
- MCP: `needrail-mcp`
- API: FastAPI on `needrail.server`
- SDK: `NeedRailClient`
- CLI: `needrail-cli`
