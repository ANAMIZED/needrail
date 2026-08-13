"""NeedRail registry — simple, provenance-first, file-backed for Phase 1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import (
    Need,
    NeedStatus,
    NeedType,
    Project,
    Provenance,
    Receipt,
    ReceiptType,
    Wallet,
    Amount,
    utcnow,
    new_id,
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"
NEEDS_FILE = DATA_DIR / "needs.json"
RECEIPTS_FILE = DATA_DIR / "receipts.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load(path: Path, model):
    if not path.exists():
        return []
    with open(path) as f:
        raw = json.load(f)
    return [model.model_validate(item) for item in raw]


def _save(path: Path, items: list) -> None:
    _ensure_data_dir()
    with open(path, "w") as f:
        json.dump([i.model_dump(mode="json", by_alias=True) for i in items], f, indent=2, default=str)


class Registry:
    def __init__(self) -> None:
        _ensure_data_dir()
        self.projects: list[Project] = _load(PROJECTS_FILE, Project)
        self.needs: list[Need] = _load(NEEDS_FILE, Need)
        self.receipts: list[Receipt] = _load(RECEIPTS_FILE, Receipt)
        if not self.projects:
            self._seed()

    def _seed(self) -> None:
        """Seed with a high-signal public-goods example."""
        proj = Project(
            id="needrail-core",
            name="NeedRail",
            description="Get what you NEED to succeed & do agentic public good. Protocol-native coordination for agents and open systems.",
            homepage="https://github.com/ANAMIZED/needrail",
            repository="https://github.com/ANAMIZED/needrail",
            license="Apache-2.0",
            maintainers=["needrail"],
            tags=["public-goods", "agents", "mcp", "x402", "coordination"],
            funding_wallets=[Wallet(chain="eip155:8453", address="0x0000000000000000000000000000000000000000", asset="USDC")],
            provenance=Provenance(source="seed", attested_by="needrail"),
        )
        self.projects.append(proj)

        need = Need(
            id="need-001",
            project_id=proj.id,
            requester="needrail",
            type=NeedType.feature,
            title="Ship Phase-1 vertical slice",
            description="Working MCP tools + x402 support endpoint + receipt write-back so any agent can discover, fund, and complete Needs.",
            amount_or_bounty=Amount(target="100", asset="USDC", network="eip155:8453", partial_ok=True),
            acceptance_criteria=[
                "MCP list_needs / get_need / create_need callable",
                "x402 402 response with payment requirements",
                "Receipt written back into registry after simulated settlement",
            ],
            pay_to=[Wallet(chain="eip155:8453", address="0x0000000000000000000000000000000000000000", asset="USDC")],
            status=NeedStatus.open,
            provenance=Provenance(source="seed", attested_by="needrail"),
        )
        self.needs.append(need)
        self._persist()

    def _persist(self) -> None:
        _save(PROJECTS_FILE, self.projects)
        _save(NEEDS_FILE, self.needs)
        _save(RECEIPTS_FILE, self.receipts)

    def list_projects(self, tag: Optional[str] = None) -> list[Project]:
        if tag:
            return [p for p in self.projects if tag in p.tags]
        return list(self.projects)

    def get_project(self, project_id: str) -> Optional[Project]:
        for p in self.projects:
            if p.id == project_id:
                return p
        return None

    def list_needs(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        project_id: Optional[str] = None,
        requester: Optional[str] = None,
    ) -> list[Need]:
        result = self.needs
        if status:
            result = [n for n in result if n.status.value == status]
        if type:
            result = [n for n in result if n.type.value == type]
        if project_id:
            result = [n for n in result if n.project_id == project_id]
        if requester:
            result = [n for n in result if n.requester == requester]
        return result

    def get_need(self, need_id: str) -> Optional[Need]:
        for n in self.needs:
            if n.id == need_id:
                return n
        return None

    def create_need(self, need: Need) -> Need:
        self.needs.append(need)
        self._persist()
        return need

    def update_need(self, need: Need) -> Need:
        for i, n in enumerate(self.needs):
            if n.id == need.id:
                need.updated_at = utcnow()
                self.needs[i] = need
                self._persist()
                return need
        raise KeyError(f"Need {need.id} not found")

    def claim_need(self, need_id: str, claimer: str) -> Need:
        need = self.get_need(need_id)
        if not need:
            raise KeyError(f"Need {need_id} not found")
        if need.status not in (NeedStatus.open, NeedStatus.funded):
            raise ValueError(f"Need {need_id} is not claimable (status={need.status})")
        need.claimed_by = claimer
        need.status = NeedStatus.in_progress
        return self.update_need(need)

    def complete_need(self, need_id: str, evidence_links: list[str], completer: str) -> Need:
        need = self.get_need(need_id)
        if not need:
            raise KeyError(f"Need {need_id} not found")
        need.evidence_links.extend(evidence_links)
        need.status = NeedStatus.completed
        need.completed_at = utcnow()
        need = self.update_need(need)

        receipt = Receipt(
            type=ReceiptType.completion,
            need_id=need.id,
            project_id=need.project_id,
            from_entity=completer,
            to_entity=need.requester,
            evidence=evidence_links,
            provenance=Provenance(source="needrail.complete_need", attested_by=completer),
        )
        self.add_receipt(receipt)
        return need

    def add_receipt(self, receipt: Receipt) -> Receipt:
        self.receipts.append(receipt)
        self._persist()
        return receipt

    def get_receipts(self, need_id: Optional[str] = None, project_id: Optional[str] = None) -> list[Receipt]:
        result = self.receipts
        if need_id:
            result = [r for r in result if r.need_id == need_id]
        if project_id:
            result = [r for r in result if r.project_id == project_id]
        return result


_registry: Optional[Registry] = None


def get_registry() -> Registry:
    global _registry
    if _registry is None:
        _registry = Registry()
    return _registry
