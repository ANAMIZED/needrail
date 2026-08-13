# NeedRail Roadmap — Future-Proof & Trust-First

**Positioning (locked):**  
NeedRail is the OSS / public-goods profile of the agent-commerce stack.  
It composes x402 + MCP + ERC-8004 + EAS / ERC-8183 into a first-class **Need** object that is MCP-native, provenance-mandatory, and optimized for open-source work.

**North star:** Zero mandatory platform intermediary.  
Maintainer attestation and independent verification are features, not failures of purity.

---

## Phase 0 — Foundation (Shipped)

- Public repository
- MCP surface (full Need lifecycle tools)
- Real HTTP 402 Payment Required endpoint
- Content-addressed storage primitives (`cas.py`)
- Reference agent that dogfoods the loop
- AGENTS.md + SKILL.md
- Non-custodial default
- Apache-2.0

---

## Phase 1 — Trust Infrastructure (Shipped)

| # | Item | Status | Location |
|---|------|--------|----------|
| 1 | Honest repositioning | Done | README + this file |
| 2 | Identity binding (ERC-8004 / DID) | Done | `adapters/erc8004.py` |
| 3 | Prompt-injection hardening | Done | `security.py` |
| 4 | Optional non-custodial escrow | Done | `adapters/erc8183.py` |
| 5 | Attestation mapping (EAS) | Done | `adapters/eas.py` |
| 6 | Discovery composition | Done | `docs/DISCOVERY.md` |
| 7 | x402 facilitator client | Done | `x402.py` |

**Hardened acceptance path:** `examples/hardened_reference_agent.py`  
Requires independent evaluator attestation before treating payment as fully trusted.

---

## Phase 2 — Trust Density (In progress)

| Item | Status |
|------|--------|
| Economic anti-spam deposits | Done — `adapters/antispam.py` |
| Staked / independent completion verification | Interface ready via escrow evaluator |
| Evidence-weighted reputation | Next |
| Partial funding, claim expiry, milestones | Partial |

---

## Phase 3 — Network Effects & Longevity

1. Federation with explicit indexer incentives  
2. On-chain anchoring of critical receipts (live EAS schema registration)  
3. Read-only import bridges  
4. Conformance suite  
5. Public ranking by provenance strength + OSS bias  

---

## Permanent Invariants

- Protocol over platform  
- Non-custodial by default  
- Provenance mandatory  
- Agents are first-class users  
- OSS / public-goods vertical remains primary  
- Compose standards; do not re-invent identity, escrow, or attestation  
- Payments are final unless an optional escrow path was chosen  
