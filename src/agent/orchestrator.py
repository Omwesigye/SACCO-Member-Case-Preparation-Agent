"""
SACCO Case Preparation Agent — Bounded Workflow Orchestrator (Week 6)

Extends the bounded agent workflow with a safe persistent-memory feature:
  1. Sense/Context  -> Checks for existing case memory, prior staff comments,
                       calculation caches, and Credit Committee decisions.
  2. Plan/Decide    -> Reuses valid calculations if input hash matches;
                       invalidates cache if inputs change or policy is stale.
  3. Act/Tool       -> Executes approved tools only for uncompleted or changed steps.
  4. Observe        -> Updates missing-document checklist and staff notes.
  5. Re-plan / Stop -> Persists safe draft state (DRAFT_INCOMPLETE or
                       DRAFT_READY_FOR_HUMAN_REVIEW). Strictly prohibited from
                       silently approving loans or overriding committee decisions.

An Audit Log records every tool call, cached retrieval, data point, calculation,
and decision timestamp.
"""

from pathlib import Path
import sys

# Ensure agent directory is in sys.path
agent_dir = Path(__file__).resolve().parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from tools import (
    retrieve_member_record,
    search_sacco_policy,
    calculate_illustrative_schedule,
    create_case_pack_draft,
)
from case_memory import (
    CaseMemoryStore,
    compute_inputs_hash,
    ACTIVE_POLICY_VERSIONS,
    MemorySafetyViolation,
)

MAX_ITERATIONS = 6
APPROVED_TOOLS = {
    "retrieve_member_record",
    "search_sacco_policy",
    "calculate_illustrative_schedule",
    "create_case_pack_draft",
}


class AuditLog:
    """Mirrors the diagram's Audit Log box: tools called, data retrieved,
    calculations performed, decisions/planning steps, timestamps & results."""

    def __init__(self):
        self.entries = []

    def record(self, tool, inputs, result, source="tool_execution"):
        self.entries.append({
            "tool": tool,
            "inputs": inputs,
            "result": result,
            "source": source
        })

    def to_list(self):
        return self.entries


class AgentTrace:
    def __init__(self, member_id, case_id=None):
        self.member_id = member_id
        self.case_id = case_id
        self.steps = []
        self.status = "IN_PROGRESS"
        self.audit_log = AuditLog()
        self.cached_calculations_reused = 0
        self.tool_calculations_executed = 0

    def log(self, step_name, sense, plan, act, observe):
        self.steps.append({
            "step": len(self.steps) + 1,
            "name": step_name,
            "sense": sense,
            "plan": plan,
            "act": act,
            "observe": observe,
        })

    def replan(self, reason, new_plan):
        self.steps.append({
            "step": len(self.steps) + 1,
            "name": "RE-PLAN",
            "sense": None,
            "plan": f"Information insufficient ({reason}). New plan: {new_plan}",
            "act": None,
            "observe": None,
        })

    def stop(self, status, reason):
        self.status = status
        self.steps.append({
            "step": len(self.steps) + 1,
            "name": "STOP",
            "sense": None,
            "plan": None,
            "act": None,
            "observe": {
                "status": status,
                "reason": reason,
                "note": "Not an approval or rejection decision.",
            },
        })

    def to_text(self):
        header = f"EXECUTION TRACE — member_id={self.member_id}"
        if self.case_id:
            header += f" | case_id={self.case_id}"
        lines = [header, "=" * 60]
        for s in self.steps:
            lines.append(f"\nStep {s['step']}: {s['name']}")
            for key in ("sense", "plan", "act", "observe"):
                if s[key] is not None:
                    label = {
                        "sense": "Sense/Context",
                        "plan": "Plan/Decide",
                        "act": "Act/Tool",
                        "observe": "Observe",
                    }[key]
                    lines.append(f"  {label:<14}: {s[key]}")
        lines.append(f"\nFinal status: {self.status}")
        lines.append(
            f"Calculations summary: {self.cached_calculations_reused} reused from memory, "
            f"{self.tool_calculations_executed} computed freshly"
        )
        lines.append(f"\nAudit Log ({len(self.audit_log.entries)} entries):")
        for e in self.audit_log.entries:
            lines.append(f"  - [{e.get('source', 'tool')}] {e['tool']}(inputs={e['inputs']}) -> {e['result']}")
        return "\n".join(lines)


def run_case_preparation(
    member_id: str,
    case_id: str = None,
    officer_comment: str = None,
    officer_id: str = "LO-001",
    memory_store: CaseMemoryStore = None,
    override_policy_version: dict = None,
) -> AgentTrace:
    """
    Executes the bounded SACCO case-preparation workflow with persistent memory.

    Args:
        member_id: Target member ID (e.g. 'SACCO-M-001').
        case_id: Optional case ID. If omitted, derives or fetches latest for member.
        officer_comment: Optional narrative review comment from the loan officer.
        officer_id: Identifier of the loan officer interacting with the case.
        memory_store: CaseMemoryStore instance (defaults to persistent store).
        override_policy_version: Used in testing to simulate stale policy detection.
    """
    if memory_store is None:
        memory_store = CaseMemoryStore()

    # Determine or load case memory
    existing_case = None
    if case_id:
        existing_case = memory_store.get_case(case_id)
    else:
        existing_case = memory_store.get_latest_case_for_member(member_id)
        if existing_case:
            case_id = existing_case.get("case_id")

    if not case_id:
        case_id = f"CASE-2026-{abs(hash(member_id)) % 10000:04d}"

    trace = AgentTrace(member_id=member_id, case_id=case_id)
    iteration = 0

    # =========================================================================
    # SAFETY INVARIANT 3: Check for existing Credit Committee Decision
    # =========================================================================
    if existing_case and existing_case.get("committee_decision") is not None:
        comm_dec = existing_case["committee_decision"]
        trace.stop(
            "STOPPED_COMMITTEE_DECISION_FINAL",
            f"Case '{case_id}' already has a final Credit Committee decision "
            f"({comm_dec.get('decision')} on {comm_dec.get('timestamp')}). "
            "Safety Invariant 3 Enforced: Agent persistent memory cannot modify or reopen a concluded case."
        )
        return trace

    # =========================================================================
    # 1. Sense/Context: Load persistent memory if available
    # =========================================================================
    iteration += 1
    cached_calcs = {}
    cached_policy = {}
    staff_comments = []

    if existing_case:
        cached_calcs = existing_case.get("calculations_cache", {})
        cached_policy = existing_case.get("policy_versions_used", {})
        staff_comments = list(existing_case.get("staff_comments", []))

    if officer_comment:
        staff_comments.append({
            "officer_id": officer_id,
            "timestamp": "2026-10-12T20:00:00Z",
            "note": officer_comment,
        })

    trace.log(
        "Sense case memory & context",
        sense=f"Preparing case '{case_id}' for member '{member_id}'. "
              f"Prior memory loaded: {len(cached_calcs)} cached calculations, "
              f"{len(staff_comments)} staff comments.",
        plan="Retrieve current member record and compare against memory cache",
        act="retrieve_member_record(member_id)",
        observe=None,
    )

    member = retrieve_member_record(member_id)
    trace.audit_log.record("retrieve_member_record", {"member_id": member_id}, member)
    trace.steps[-1]["observe"] = member

    if not member.get("record_found"):
        trace.stop(
            "STOPPED_INCOMPLETE",
            f"Member record not found or invalid ({member.get('error')}). "
            "Agent stops rather than guessing member data; hand off to staff."
        )
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # =========================================================================
    # 2. Policy Evidence Retrieval (SAFETY INVARIANT 2: Staleness Guard)
    # =========================================================================
    iteration += 1
    topics = ["eligibility", "dsr", "kyc", "guarantor"]

    # Use simulated policy version if provided (for testing staleness), otherwise active
    active_policy = override_policy_version if override_policy_version is not None else ACTIVE_POLICY_VERSIONS
    policy_is_stale = CaseMemoryStore.is_policy_stale(cached_policy) or (cached_policy != active_policy)

    if not policy_is_stale and existing_case and "policy_evidence" in existing_case:
        policy = {"evidence_found": True, "evidence": existing_case["policy_evidence"]}
        trace.log(
            "Verify policy evidence",
            sense=f"Persistent memory references current policy versions: {cached_policy}",
            plan="Reuse validated policy evidence from memory cache; no policy changes detected",
            act="reused_from_memory(policy_evidence)",
            observe=f"Reused {len(policy['evidence'])} verified policy snippets",
        )
        trace.audit_log.record("search_sacco_policy", {"topics": topics}, policy, source="memory_cache")
    else:
        trace.log(
            "Retrieve policy evidence",
            sense="Policy cache empty or stale; fresh policy retrieval required to ensure compliance",
            plan=f"Call search_sacco_policy() for topics: {topics}",
            act="search_sacco_policy(topics)",
            observe=None,
        )
        policy = search_sacco_policy(topics)
        trace.audit_log.record("search_sacco_policy", {"topics": topics}, policy, source="tool_execution")
        trace.steps[-1]["observe"] = policy

    if not policy.get("evidence_found"):
        trace.stop("STOPPED_INCOMPLETE", "No relevant policy evidence retrieved. Agent stops.")
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # =========================================================================
    # 3. Deterministic Calculations with Memory Continuity & Input Hashing
    # =========================================================================
    iteration += 1
    applicable = []
    if member.get("requested_loan") and member.get("requested_term_months"):
        applicable.append("repayment_schedule")
    if member.get("monthly_income") is not None:
        applicable.append("debt_service_ratio")
    if member.get("savings_balance") is not None:
        applicable.append("savings_loan_limit")

    trace.log(
        "Evaluate required calculations",
        sense=f"Identified applicable calculations: {applicable}. "
              "Checking persistent memory cache against current member parameters...",
        plan="Reuse unchanged calculations from memory; only compute if inputs changed or missing",
        act="evaluate_calculation_cache()",
        observe=None,
    )

    calc_results = {}
    calc_failed = None
    new_cache = dict(cached_calcs)

    # 3A. Repayment Schedule
    if "repayment_schedule" in applicable:
        rep_inputs = {
            "principal": member["requested_loan"],
            "annual_interest_rate": member["annual_interest_rate"],
            "term_months": member["requested_term_months"],
        }
        rep_hash = compute_inputs_hash(rep_inputs)
        cached_entry = cached_calcs.get("repayment_schedule")

        if cached_entry and cached_entry.get("inputs_hash") == rep_hash and not policy_is_stale:
            # CACHE HIT
            calc_results["repayment_schedule"] = cached_entry["result"]
            trace.cached_calculations_reused += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "repayment_schedule", **rep_inputs},
                cached_entry["result"],
                source="persistent_memory_cache",
            )
        else:
            # CACHE MISS OR INPUTS CHANGED
            res = calculate_illustrative_schedule("repayment_schedule", rep_inputs)
            trace.tool_calculations_executed += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "repayment_schedule", **rep_inputs},
                res,
                source="tool_execution",
            )
            if not res.get("calculation_successful"):
                calc_failed = res
            else:
                calc_results["repayment_schedule"] = res
                new_cache["repayment_schedule"] = {
                    "inputs_hash": rep_hash,
                    "inputs": rep_inputs,
                    "result": res,
                }

    # 3B. Debt Service Ratio (DSR)
    if not calc_failed and "debt_service_ratio" in applicable:
        proposed_monthly = (
            calc_results.get("repayment_schedule", {}).get("result", {}).get("monthly_payment", 0)
        )
        dsr_inputs = {
            "net_monthly_income": member["monthly_income"],
            "existing_monthly_obligations": member["existing_monthly_obligations"],
            "proposed_monthly_installment": proposed_monthly,
        }
        dsr_hash = compute_inputs_hash(dsr_inputs)
        cached_entry = cached_calcs.get("debt_service_ratio")

        if cached_entry and cached_entry.get("inputs_hash") == dsr_hash and not policy_is_stale:
            # CACHE HIT
            calc_results["debt_service_ratio"] = cached_entry["result"]
            trace.cached_calculations_reused += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "debt_service_ratio", **dsr_inputs},
                cached_entry["result"],
                source="persistent_memory_cache",
            )
        else:
            # CACHE MISS OR INPUTS CHANGED
            res = calculate_illustrative_schedule("debt_service_ratio", dsr_inputs)
            trace.tool_calculations_executed += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "debt_service_ratio", **dsr_inputs},
                res,
                source="tool_execution",
            )
            if not res.get("calculation_successful"):
                calc_failed = res
            else:
                calc_results["debt_service_ratio"] = res
                new_cache["debt_service_ratio"] = {
                    "inputs_hash": dsr_hash,
                    "inputs": dsr_inputs,
                    "result": res,
                }

    # 3C. Savings Loan Limit
    if not calc_failed and "savings_loan_limit" in applicable:
        sav_inputs = {
            "savings_balance": member["savings_balance"],
            "multiplier_rate": 3,
        }
        sav_hash = compute_inputs_hash(sav_inputs)
        cached_entry = cached_calcs.get("savings_loan_limit")

        if cached_entry and cached_entry.get("inputs_hash") == sav_hash and not policy_is_stale:
            # CACHE HIT
            calc_results["savings_loan_limit"] = cached_entry["result"]
            trace.cached_calculations_reused += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "savings_loan_limit", **sav_inputs},
                cached_entry["result"],
                source="persistent_memory_cache",
            )
        else:
            # CACHE MISS
            res = calculate_illustrative_schedule("savings_loan_limit", sav_inputs)
            trace.tool_calculations_executed += 1
            trace.audit_log.record(
                "calculate_illustrative_schedule",
                {"calculation_type": "savings_loan_limit", **sav_inputs},
                res,
                source="tool_execution",
            )
            if not res.get("calculation_successful"):
                calc_failed = res
            else:
                calc_results["savings_loan_limit"] = res
                new_cache["savings_loan_limit"] = {
                    "inputs_hash": sav_hash,
                    "inputs": sav_inputs,
                    "result": res,
                }

    trace.steps[-1]["observe"] = {
        "calculations_available": list(calc_results.keys()),
        "reused_from_cache": trace.cached_calculations_reused,
        "newly_computed": trace.tool_calculations_executed,
    }

    if calc_failed:
        trace.stop("STOPPED_ERROR", f"Calculation failed: {calc_failed.get('error')}")
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # =========================================================================
    # 4. Assess Completeness & Missing Documents Checklist
    # =========================================================================
    iteration += 1
    kyc_is_verified = (member.get("kyc_status") == "verified")
    missing_docs = []
    if not kyc_is_verified:
        missing_docs.append("National ID (NIN) verification & LC1 Chairperson letter")

    checklist = {
        "member_record_retrieved": True,
        "policy_evidence_retrieved": True,
        "calculations_completed": len(calc_results) == len(applicable),
        "kyc_verified": kyc_is_verified,
        "has_arrears": member.get("has_arrears", False),
        "guarantors_declared": member.get("number_of_guarantors", 0) >= 2,
        "missing_documents": missing_docs,
    }

    is_complete = (
        checklist["member_record_retrieved"]
        and checklist["policy_evidence_retrieved"]
        and checklist["calculations_completed"]
        and checklist["kyc_verified"]
    )

    trace.log(
        "Assess checklist & document completeness",
        sense=f"Current documentation status: KYC verified={kyc_is_verified}, "
              f"Missing documents={missing_docs}",
        plan="Evaluate whether case meets criteria for draft review or requires further documentation",
        act="evaluate_checklist()",
        observe=checklist,
    )

    # =========================================================================
    # 5. Persist State to Case Memory (SAFETY INVARIANTS 1 & 3 ENFORCED)
    # =========================================================================
    case_record = {
        "case_id": case_id,
        "member_id": member_id,
        "policy_versions_used": ACTIVE_POLICY_VERSIONS,
        "policy_evidence": policy.get("evidence", []),
        "calculations_cache": new_cache,
        "checklist_status": checklist,
        "staff_comments": staff_comments,
        "committee_decision": None,
        "status": "DRAFT_READY_FOR_HUMAN_REVIEW" if is_complete else "DRAFT_INCOMPLETE",
    }

    # Persist via CaseMemoryStore (validates status and committee decision invariants)
    memory_store.save_case(case_record, is_agent_action=True)

    if not is_complete:
        trace.stop(
            "STOPPED_INCOMPLETE",
            f"Case saved to persistent memory as DRAFT_INCOMPLETE. "
            f"Missing requirements: {missing_docs}. "
            "Staff comments preserved; ready to resume once documents are submitted."
        )
        return trace

    # =========================================================================
    # 6. Final Draft Creation & Safe Hand-Off
    # =========================================================================
    iteration += 1
    draft_result = create_case_pack_draft(
        member_id=member["member_id"],
        policy_evidence=policy["evidence"],
        calculations=calc_results,
    )
    trace.audit_log.record(
        "create_case_pack_draft",
        {"member_id": member["member_id"], "case_id": case_id},
        draft_result,
        source="tool_execution",
    )
    trace.log(
        "Prepare draft case brief",
        sense="All required data, policy evidence, and calculations are present",
        plan="Assemble draft case pack for human officer review",
        act="create_case_pack_draft(...)",
        observe=draft_result,
    )

    trace.status = "READY_FOR_REVIEW"
    trace.steps.append({
        "step": len(trace.steps) + 1,
        "name": "STOP (safe hand-off)",
        "sense": "Case pack assembled and stored in persistent memory",
        "plan": "Hand off to human Loan Officer; strictly no automated lending decision",
        "act": None,
        "observe": {
            "status": "READY_FOR_REVIEW",
            "case_id": case_id,
            "case_pack_id": draft_result.get("case_pack_id"),
            "note": "Not an approval or rejection decision. Loan decision authority remains with humans.",
        },
    })

    return trace
