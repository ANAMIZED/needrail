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

## Phase 1 — Trust Infrastructure (Current Focus)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | Honest repositioning | Done | This document + updated README |
| 2 | Identity binding interface | In progress | ERC-8004 / DID fields on Need & Project; cost-to-create guidance |
| 3 | Prompt-injection hardening | In progress | Spending policies, untrusted content treatment, pre-execution filters |
| 4 | Optional non-custodial escrow | Spec'd | Default = direct-to-pay_to; optional path via ERC-8183-style job escrow + evaluator |
| 5 | Attestation mapping | Spec'd | Receipts designed to map cleanly to EAS or ERC-8183 evaluator attestations |
| 6 | Discovery composition | Planned | Publish into x402 Bazaar / Agentic.market + MCP Registry |
| 7 | x402 v2 + audited facilitators | Planned | Prefer open facilitators; never hand-roll settlement verification |

**Phase 1 acceptance test:**  
An external agent completes a realistic OSS Need with an *independently attested* completion (maintainer or evaluator), not pure self-attestation.

---

## Phase 2 — Trust Density

1. Staked / independent completion verification  
   - Maintainer attestation (GitHub PR merge as first-class evidence)  
   - Optional re-execution / TEE / zk paths for machine-checkable work  
2. Economic anti-spam  
   - Refundable stake or deposit on `create_need` and `claim_need`  
3. Evidence-weighted reputation  
   - Independent attestors > raw self-completed count/value  
   - Anomaly / collusion signals  
4. Partial funding, claim expiry, milestones (already partially present)

---

## Phase 3 — Network Effects & Longevity

1. Federation with explicit indexer incentives  
2. On-chain anchoring of critical receipts  
3. Read-only import bridges (GitHub Sponsors, Open Collective, Algora, Merit-style bounties)  
4. Conformance suite + hardened reference agents  
5. Public ranking surface by provenance strength + OSS bias

---

## Permanent Invariants

- Protocol over platform  
- Non-custodial by default  
- Provenance mandatory  
- Agents are first-class users  
- OSS / public-goods vertical remains primary  
- Compose standards; do not re-invent identity, escrow, or attestation  
- Payments are final unless an optional escrow path was chosen  

---

## Competitive Reality

Merit Systems remains the primary competitive signal on the OSS-funding vertical.  
Differentiation comes from attestation-native provenance, honest trust design, and strict MCP-first schemas — not from claiming to be a new primitive.

ERC-8004 is live but empirically weak on reputation (high Sybil rates). Treat it as identity infrastructure, not finished trust.  
ERC-8183 provides the missing job-escrow + evaluator pattern. Prefer composition over reinvention.
