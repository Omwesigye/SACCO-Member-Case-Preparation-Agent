"""
Case Memory Store for the SACCO Member-Case Preparation Agent.

Implements safe, bounded persistence as defined:
  - Preserves prior calculation outputs, policy version provenance,
    missing-document checklists, and loan officer review notes.
  - Enforces three negative safety invariants:
      1. Cannot silently approve a loan (agent status strictly restricted to draft/review).
      2. Cannot change policy rules (stale policy versions trigger cache invalidation).
      3. Cannot override a human Credit Committee decision (committee decisions are immutable).
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Active policy versions registered in the SACCO RAG Policy Corpus
ACTIVE_POLICY_VERSIONS = {
    "SACCO-CREDIT-001": "v3.0",
    "SACCO-AML-001": "v3.0",
}

# Permitted terminal statuses that the AI Agent may persist
AGENT_PERMITTED_STATUSES = {
    "IN_PROGRESS",
    "DRAFT_INCOMPLETE",
    "DRAFT_READY_FOR_HUMAN_REVIEW",
}

# Default storage path
DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent / "storage"
DEFAULT_STORAGE_FILE = DEFAULT_STORAGE_DIR / "case_history.json"


class MemorySafetyViolation(Exception):
    """Raised when an operation violates architectural memory safety invariants."""
    pass


def compute_inputs_hash(inputs: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash over normalized calculation inputs.
    Used to detect if calculation inputs are identical or if they have changed.
    """
    normalized = json.dumps(inputs, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class CaseMemoryStore:
    """
    Persistent store for SACCO loan case preparation state.
    Provides atomic read/write access to case records with invariant enforcement.
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or DEFAULT_STORAGE_FILE
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_file.exists():
            self._write_store({})

    def _read_store(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_store(self, data: Dict[str, Dict[str, Any]]) -> None:
        temp_file = self.storage_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        temp_file.replace(self.storage_file)

    def clear(self) -> None:
        """Clears all records in the store (used for test isolation)."""
        self._write_store({})

    # --------------------------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------------------------
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a case record by case_id."""
        store = self._read_store()
        return store.get(case_id)

    def get_latest_case_for_member(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the most recently updated case record for a member."""
        store = self._read_store()
        matching = [c for c in store.values() if c.get("member_id") == member_id]
        if not matching:
            return None
        matching.sort(key=lambda c: c.get("last_updated_at", ""), reverse=True)
        return matching[0]

    # --------------------------------------------------------------------------
    # Persistence & Safety Invariant Enforcement
    # --------------------------------------------------------------------------
    def save_case(self, case_record: Dict[str, Any], is_agent_action: bool = True) -> Dict[str, Any]:
        """
        Persists or updates a case record while validating safety invariants.

        Safety Invariant 1:
            Agent cannot silently set final loan status to 'APPROVED' or 'REJECTED'.
        Safety Invariant 3:
            Agent cannot overwrite or modify a case with an active Credit Committee decision.
        """
        case_id = case_record.get("case_id")
        if not case_id:
            raise ValueError("case_id is required to persist case memory.")

        store = self._read_store()
        existing = store.get(case_id)

        # Invariant 3: If Credit Committee decision exists, agent cannot overwrite or alter case
        if existing and existing.get("committee_decision") is not None and is_agent_action:
            raise MemorySafetyViolation(
                f"Safety Invariant 3 Violated: Case '{case_id}' has already received a "
                f"Credit Committee decision ({existing['committee_decision'].get('decision')}). "
                "Agent persistent memory is prohibited from altering or overwriting a committee decision."
            )

        status = case_record.get("status")
        # Invariant 1: Agent can only persist draft/review states
        if is_agent_action and status not in AGENT_PERMITTED_STATUSES:
            raise MemorySafetyViolation(
                f"Safety Invariant 1 Violated: Agent attempted to persist forbidden status '{status}'. "
                f"Agent is restricted to draft/review states: {sorted(list(AGENT_PERMITTED_STATUSES))}."
            )

        # Update metadata
        record = dict(case_record)
        now = datetime.utcnow().isoformat()
        if "created_at" not in record or not record["created_at"]:
            record["created_at"] = now
        record["last_updated_at"] = now

        store[case_id] = record
        self._write_store(store)
        return record

    def append_staff_comment(self, case_id: str, officer_id: str, note: str) -> Dict[str, Any]:
        """Appends a timestamped loan officer comment to the case history."""
        store = self._read_store()
        record = store.get(case_id)
        if not record:
            raise KeyError(f"Case '{case_id}' not found in persistent store.")

        comment = {
            "officer_id": officer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "note": note,
        }
        record.setdefault("staff_comments", []).append(comment)
        record["last_updated_at"] = datetime.utcnow().isoformat()
        store[case_id] = record
        self._write_store(store)
        return comment

    def record_committee_decision(
        self,
        case_id: str,
        decision: str,
        decided_by: str,
        rationale: str
    ) -> Dict[str, Any]:
        """
        Records a Credit Committee human decision (APPROVED, REJECTED, DEFERRED).
        This is an authorized human governance action, NOT an agent action.
        """
        allowed_decisions = {"APPROVED", "REJECTED", "DEFERRED"}
        if decision not in allowed_decisions:
            raise ValueError(f"Invalid committee decision '{decision}'. Must be one of {allowed_decisions}.")

        store = self._read_store()
        record = store.get(case_id)
        if not record:
            raise KeyError(f"Case '{case_id}' not found in persistent store.")

        decision_data = {
            "decision": decision,
            "decided_by": decided_by,
            "timestamp": datetime.utcnow().isoformat(),
            "rationale": rationale,
        }
        record["committee_decision"] = decision_data
        record["status"] = f"COMMITTEE_{decision}"
        record["last_updated_at"] = datetime.utcnow().isoformat()
        store[case_id] = record
        self._write_store(store)
        return decision_data

    # --------------------------------------------------------------------------
    # Policy Version Validation (Invariant 2)
    # --------------------------------------------------------------------------
    @staticmethod
    def is_policy_stale(stored_policy_versions: Optional[Dict[str, str]]) -> bool:
        """
        Safety Invariant 2:
        Checks whether policy versions recorded in memory match the active RAG policy corpus.
        Returns True if stored policy is outdated or missing, forcing fresh retrieval.
        """
        if not stored_policy_versions:
            return True
        for source_id, active_ver in ACTIVE_POLICY_VERSIONS.items():
            stored_ver = stored_policy_versions.get(source_id)
            if stored_ver != active_ver:
                return True
        return False
