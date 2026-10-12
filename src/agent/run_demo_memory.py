"""
Multi-Session Demonstration: Safe Persistent-Memory Feature

Demonstrates:
  1. Turn 1 (Incomplete Case): Initial intake for synthetic member SACCO-M-002.
     - Deterministic calculations run.
     - KYC missing; loan officer notes recorded.
     - State persisted safely as DRAFT_INCOMPLETE.
  2. Turn 2 (Resumed Case): Member submits KYC document.
     - Agent loads case memory.
     - Prior loan officer notes restored.
     - Valid calculation results reused (0 redundant calculation tool calls).
     - Checklist completed; advances to DRAFT_READY_FOR_HUMAN_REVIEW.
  3. Turn 3 (Governance Invariant): Human Credit Committee rejects case.
     - Subsequent agent execution blocked by Safety Invariant 3.
"""

from pathlib import Path
import sys

# Ensure src/agent and Tools directories are in python path
repo_root = Path(__file__).resolve().parents[2]
agent_dir = repo_root / "src" / "agent"
tools_dir = repo_root / "Tools"

for p in (str(agent_dir), str(tools_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from case_memory import CaseMemoryStore
from orchestrator import run_case_preparation
import data


def main():
    print("=" * 80)
    print("  SACCO CASE PREPARATION AGENT — PERSISTENT MEMORY DEMONSTRATION")
    print("=" * 80)

    # Use a clean demo memory store
    demo_store_path = agent_dir / "storage" / "demo_case_history.json"
    demo_store = CaseMemoryStore(storage_file=demo_store_path)
    demo_store.clear()

    case_id = "CASE-2026-0002"
    member_id = "SACCO-M-002"

    output_traces = []

    # --------------------------------------------------------------------------
    # TURN 1: Initial Application (Incomplete KYC)
    # --------------------------------------------------------------------------
    print("\n>>> TURN 1: Initial Application Intake (Incomplete KYC Documents)")
    officer_note_1 = "Member contacted via phone. Pledged to bring LC1 letter tomorrow 10am."
    
    trace_1 = run_case_preparation(
        member_id=member_id,
        case_id=case_id,
        officer_comment=officer_note_1,
        officer_id="LO-001",
        memory_store=demo_store,
    )
    print(f"Status: {trace_1.status}")
    print(f"Calculations newly computed: {trace_1.tool_calculations_executed}")
    print(f"Calculations reused from memory: {trace_1.cached_calculations_reused}")

    stored_1 = demo_store.get_case(case_id)
    print(f"Stored in persistent memory: status='{stored_1['status']}', comments={len(stored_1['staff_comments'])}")

    output_traces.append("########## TURN 1: INITIAL INTAKE (INCOMPLETE KYC) ##########\n" + trace_1.to_text())

    # --------------------------------------------------------------------------
    # TURN 2: Resumed Application (KYC Provided - Work Continuity)
    # --------------------------------------------------------------------------
    print("\n>>> TURN 2: Resumed Application (Member Submits LC1 Letter)")
    # Member updates KYC status in records
    data.MEMBERS["SACCO-M-002"]["kyc_status"] = "verified"

    officer_note_2 = "LC1 Chairperson letter received and verified by officer LO-001."
    trace_2 = run_case_preparation(
        member_id=member_id,
        case_id=case_id,
        officer_comment=officer_note_2,
        officer_id="LO-001",
        memory_store=demo_store,
    )
    print(f"Status: {trace_2.status}")
    print(f"Calculations newly computed: {trace_2.tool_calculations_executed}")
    print(f"Calculations reused from memory: {trace_2.cached_calculations_reused} (REDUNDANT MATH ELIMINATED)")

    stored_2 = demo_store.get_case(case_id)
    print(f"Updated in persistent memory: status='{stored_2['status']}', comments={len(stored_2['staff_comments'])}")

    output_traces.append("\n\n########## TURN 2: RESUMED INTAKE (REUSED MATH & VERIFIED KYC) ##########\n" + trace_2.to_text())

    # --------------------------------------------------------------------------
    # TURN 3: Governance Protection (Committee Verdict Lock)
    # --------------------------------------------------------------------------
    print("\n>>> TURN 3: Credit Committee Governance Decision & Agent Lock")
    demo_store.record_committee_decision(
        case_id=case_id,
        decision="REJECTED",
        decided_by="Credit Committee (3-member quorum)",
        rationale="External bureau liabilities exceed capacity.",
    )
    print("Credit Committee logged formal decision: REJECTED.")

    trace_3 = run_case_preparation(
        member_id=member_id,
        case_id=case_id,
        memory_store=demo_store,
    )
    print(f"Agent Attempt to Prepare Case: Status = {trace_3.status}")
    output_traces.append("\n\n########## TURN 3: GOVERNANCE LOCK (COMMITTEE DECISION FINAL) ##########\n" + trace_3.to_text())

    # Reset synthetic data back to original
    data.MEMBERS["SACCO-M-002"]["kyc_status"] = "missing"

    trace_file = agent_dir / "memory_demonstration_traces.txt"
    with open(trace_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_traces))

    print(f"\n[DONE] Execution traces saved to: {trace_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
