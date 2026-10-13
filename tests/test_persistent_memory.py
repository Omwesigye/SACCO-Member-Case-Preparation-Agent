"""
Automated Test Suite: Safe Persistent-Memory Feature

Verifies operational continuity and architectural safety invariants for the
SACCO Member-Case Preparation Agent's persistent memory feature:
  1. Continuity: Preserves loan officer review comments across sessions.
  2. Continuity: Reuses valid deterministic calculations when inputs are unchanged.
  3. Continuity: Recomputes calculations when member parameters change.
  4. Continuity: Incremental progression of missing-document checklist.
  5. Safety Invariant 1: Memory cannot silently approve a loan or disburse funds.
  6. Safety Invariant 2: Memory cannot change or apply stale policy rules.
  7. Safety Invariant 3: Memory cannot override a Credit Committee decision.
"""

import sys
from pathlib import Path
import pytest

# Ensure src/agent and Tools directories are in python path
repo_root = Path(__file__).resolve().parents[1]
agent_dir = repo_root / "src" / "agent"
tools_dir = repo_root / "Tools"

for p in (str(agent_dir), str(tools_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from case_memory import (
    CaseMemoryStore,
    MemorySafetyViolation,
    ACTIVE_POLICY_VERSIONS,
    compute_inputs_hash,
)
from orchestrator import run_case_preparation
from orchestration_layer import ApplicationOrchestrator, UserContext
import data


@pytest.fixture
def temp_memory_store(tmp_path):
    storage_file = tmp_path / "test_case_history.json"
    return CaseMemoryStore(storage_file=storage_file)


@pytest.fixture
def loan_officer():
    return UserContext(user_id="LO-001", role="Loan Officer", is_authenticated=True)


# ==============================================================================
# Group 1: Operational Continuity Tests
# ==============================================================================

def test_continuity_preserves_officer_comments(temp_memory_store):
    """MEM-01: Verifies narrative loan officer notes persist across sessions."""
    case_id = "CASE-TEST-001"
    note_text = "Member promised to submit LC1 residence letter by Friday 2pm."

    # Session 1: Run case preparation and append officer note
    trace1 = run_case_preparation(
        member_id="SACCO-M-002",
        case_id=case_id,
        officer_comment=note_text,
        memory_store=temp_memory_store,
    )
    assert trace1.status == "STOPPED_INCOMPLETE"

    # Verify note in persistent store
    stored = temp_memory_store.get_case(case_id)
    assert stored is not None
    assert len(stored["staff_comments"]) == 1
    assert stored["staff_comments"][0]["note"] == note_text

    # Session 2: Resumed by another loan officer with a second comment
    second_note = "Received LC1 letter copy; pending NIN confirmation."
    trace2 = run_case_preparation(
        member_id="SACCO-M-002",
        case_id=case_id,
        officer_comment=second_note,
        officer_id="LO-002",
        memory_store=temp_memory_store,
    )
    stored2 = temp_memory_store.get_case(case_id)
    assert len(stored2["staff_comments"]) == 2
    assert stored2["staff_comments"][0]["note"] == note_text
    assert stored2["staff_comments"][1]["note"] == second_note


def test_continuity_reuses_valid_calculations(temp_memory_store):
    """MEM-02: Verifies identical member parameters reuse cached calculations (0 redundant tool calls)."""
    case_id = "CASE-TEST-002"

    # Turn 1: Initial preparation executes deterministic calculation tools
    trace1 = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace1.tool_calculations_executed >= 2
    assert trace1.cached_calculations_reused == 0

    # Turn 2: Reopen identical case. Memory detects matching input hashes.
    trace2 = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace2.tool_calculations_executed == 0
    assert trace2.cached_calculations_reused >= 2

    # Verify calculation results match exactly
    stored = temp_memory_store.get_case(case_id)
    assert "repayment_schedule" in stored["calculations_cache"]
    assert stored["calculations_cache"]["repayment_schedule"]["result"]["calculation_successful"] is True


def test_continuity_recalculates_when_inputs_change(temp_memory_store, monkeypatch):
    """MEM-03: Verifies changing member inputs invalidates cache and triggers fresh calculation."""
    case_id = "CASE-TEST-003"

    # Turn 1: Run with original loan request (6,000,000 UGX)
    trace1 = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    stored1 = temp_memory_store.get_case(case_id)
    orig_hash = stored1["calculations_cache"]["repayment_schedule"]["inputs_hash"]

    # Member modifies loan request to 8,000,000 UGX
    modified_member = dict(data.MEMBERS["SACCO-M-001"])
    modified_member["requested_loan"] = 8000000
    monkeypatch.setitem(data.MEMBERS, "SACCO-M-001", modified_member)

    # Turn 2: Agent detects input hash mismatch, re-runs deterministic calculation
    trace2 = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace2.tool_calculations_executed >= 1

    stored2 = temp_memory_store.get_case(case_id)
    new_hash = stored2["calculations_cache"]["repayment_schedule"]["inputs_hash"]
    assert new_hash != orig_hash


def test_continuity_incremental_checklist_progression(temp_memory_store, monkeypatch):
    """MEM-04: Verifies incremental progression from DRAFT_INCOMPLETE to READY_FOR_REVIEW upon document arrival."""
    case_id = "CASE-TEST-004"

    # Session 1: Member SACCO-M-002 has kyc_status='missing'
    trace1 = run_case_preparation(
        member_id="SACCO-M-002",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace1.status == "STOPPED_INCOMPLETE"
    stored1 = temp_memory_store.get_case(case_id)
    assert stored1["status"] == "DRAFT_INCOMPLETE"
    assert len(stored1["checklist_status"]["missing_documents"]) > 0

    # Member submits KYC documents -> status becomes 'verified'
    verified_member = dict(data.MEMBERS["SACCO-M-002"])
    verified_member["kyc_status"] = "verified"
    monkeypatch.setitem(data.MEMBERS, "SACCO-M-002", verified_member)

    # Session 2: Resumed case reuses calculations and completes checklist
    trace2 = run_case_preparation(
        member_id="SACCO-M-002",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace2.status == "READY_FOR_REVIEW"
    assert trace2.cached_calculations_reused >= 2

    stored2 = temp_memory_store.get_case(case_id)
    assert stored2["status"] == "DRAFT_READY_FOR_HUMAN_REVIEW"
    assert len(stored2["checklist_status"]["missing_documents"]) == 0


# ==============================================================================
# Group 2: Safety Invariant Tests
# ==============================================================================

def test_safety_invariant_1_memory_cannot_silently_approve(temp_memory_store, loan_officer):
    """SAFE-01: Verifies agent memory cannot set terminal 'APPROVED' status or call forbidden tools."""
    # Sub-test 1A: Attempt to persist an 'APPROVED' status from agent action
    with pytest.raises(MemorySafetyViolation) as exc_info:
        temp_memory_store.save_case({
            "case_id": "CASE-FORBIDDEN-01",
            "member_id": "SACCO-M-001",
            "status": "APPROVED",  # Prohibited!
        }, is_agent_action=True)
    assert "Safety Invariant 1 Violated" in str(exc_info.value)

    # Sub-test 1B: Orchestration layer blocks autonomous loan approval
    orch = ApplicationOrchestrator()
    res = orch.execute_tool(
        tool_name="approveLoan",
        parameters={"application_id": "APP-1001"},
        user=loan_officer,
    )
    assert res["status"] == "FORBIDDEN_OPERATION"
    assert "human" in res["message"].lower()


def test_safety_invariant_2_stale_policy_forces_fresh_retrieval(temp_memory_store):
    """SAFE-02: Verifies memory referencing outdated policy version (v2.0) forces fresh policy retrieval."""
    case_id = "CASE-STALE-001"

    # Pre-populate memory with deprecated policy version v2.0
    stale_record = {
        "case_id": case_id,
        "member_id": "SACCO-M-001",
        "created_at": "2026-09-01T10:00:00Z",
        "policy_versions_used": {
            "SACCO-CREDIT-001": "v2.0",  # Outdated version!
            "SACCO-AML-001": "v2.0",
        },
        "policy_evidence": [{"topic": "dsr", "text": "Deprecated 60% rule"}],
        "calculations_cache": {},
        "checklist_status": {},
        "staff_comments": [],
        "committee_decision": None,
        "status": "DRAFT_INCOMPLETE",
    }
    temp_memory_store.save_case(stale_record, is_agent_action=False)

    # Agent executes with active corpus v3.0
    trace = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )

    # Assert fresh retrieval was performed rather than using deprecated v2.0 cache
    policy_calls = [e for e in trace.audit_log.entries if e["tool"] == "search_sacco_policy"]
    assert any(c.get("source") == "tool_execution" for c in policy_calls)

    updated_case = temp_memory_store.get_case(case_id)
    assert updated_case["policy_versions_used"]["SACCO-CREDIT-001"] == "v3.0"


def test_safety_invariant_3_cannot_override_committee_decision(temp_memory_store):
    """SAFE-03: Verifies agent persistent memory cannot modify or override a Credit Committee decision."""
    case_id = "CASE-GOVERNANCE-001"

    # Setup case in memory
    initial_case = {
        "case_id": case_id,
        "member_id": "SACCO-M-001",
        "created_at": "2026-10-10T10:00:00Z",
        "status": "DRAFT_READY_FOR_HUMAN_REVIEW",
    }
    temp_memory_store.save_case(initial_case, is_agent_action=True)

    # Credit Committee reviews and records an official REJECTED decision
    temp_memory_store.record_committee_decision(
        case_id=case_id,
        decision="REJECTED",
        decided_by="Credit Committee (3-member quorum)",
        rationale="Over-indebtedness identified on external obligations.",
    )

    # Sub-test 3A: Agent execution on this case is immediately blocked
    trace = run_case_preparation(
        member_id="SACCO-M-001",
        case_id=case_id,
        memory_store=temp_memory_store,
    )
    assert trace.status == "STOPPED_COMMITTEE_DECISION_FINAL"
    assert "Safety Invariant 3 Enforced" in trace.steps[-1]["observe"]["reason"]

    # Sub-test 3B: Direct attempt to overwrite via memory_store.save_case() raises safety exception
    with pytest.raises(MemorySafetyViolation) as exc_info:
        temp_memory_store.save_case({
            "case_id": case_id,
            "member_id": "SACCO-M-001",
            "status": "DRAFT_INCOMPLETE",
        }, is_agent_action=True)
    assert "Safety Invariant 3 Violated" in str(exc_info.value)


# ==============================================================================
# Standalone Runner
# ==============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("  RUNNING SAFE PERSISTENT MEMORY TEST SUITE")
    print("=" * 75)
    pytest.main([__file__, "-v"])
