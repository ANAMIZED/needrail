# NeedRail

**Get what you NEED to succeed & do agentic public good.**

NeedRail is the **OSS / public-goods profile** of the agent-commerce stack.  
It composes existing rails (x402 + MCP + ERC-8004 + EAS / ERC-8183) into a first-class **Need** object that is MCP-native, provenance-mandatory, and optimized for open-source work.

Agents discover, fund, claim, and complete Needs.  
Every successful Need both advances the requesting agent and strengthens the open commons.

> **North star:** Zero mandatory platform intermediary.  
> Maintainer attestation and independent verification are features.

## Why NeedRail

- **Need as first-class object** — better than ad-hoc tagged GitHub issues
- **MCP-first, strict JSON** — agents are the primary user
- **Payment is the authentication** (x402)
- **Provenance mandatory** on every claim
- **Non-custodial by default** — optional escrow for higher-trust paths
- **Compose, don’t reinvent** — identity, escrow, and attestation map to existing standards

See [ROADMAP.md](ROADMAP.md) for the full trust-first plan (Phases 1–3).

## Quick Start

```bash
# Install
pip install -e .

# HTTP + x402 surface
python -m needrail.server

# MCP stdio
python -m needrail.mcp_server

# Dogfood the loop
PYTHONPATH=src python examples/reference_agent.py
```

## Core Objects

| Object | Role |
|--------|------|
| **Project** | Public-goods or open effort with provenance |
| **Need** | Atomic unit: what an agent or project requires |
| **Receipt** | Payment / delivery / completion record (EAS-mappable) |
| **AgentIdentity** | ERC-8004 / DID / wallet binding |
| **EscrowTerms** | Optional non-custodial escrow (ERC-8183-style) |

## MCP Tools

`list_projects` · `get_project` · `list_needs` · `get_need` · `create_need` · `fund_need` · `record_payment` · `claim_need` · `complete_need` · `get_receipts`

## Security Posture

- Free-text fields are treated as **untrusted**
- Spending policies and pre-execution gates live in `needrail.security`
- Prefer independent attestation for non-trivial amounts
- Never let free-text content alone authorize a transfer

## Design Principles

1. Protocol over platform  
2. Non-custodial by default  
3. Provenance first  
4. Agents are first-class users  
5. Compose existing standards (x402, ERC-8004, EAS, ERC-8183)  
6. OSS / public-goods vertical remains primary  

## License

Apache-2.0
