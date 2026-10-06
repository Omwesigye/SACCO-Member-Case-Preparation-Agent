"""
SACCO Case Preparation Agent — Bounded Workflow Orchestrator (Week 5)

Matches the group's Agent Architecture Diagram exactly:
  1. Sense/Context
  2. Plan/Decide
  3. Act/Tool  -> retrieve_member_record(), search_sacco_policy(),
                   calculate_illustrative_schedule(), create_case_pack_draft()
  4. Observe
  5. Re-plan (loop back to Plan/Decide if information is insufficient)
  6. Stop     -> case pack complete, ready for review; NOT an approval
                  or rejection decision

An Audit Log records every tool call, data point, calculation and
decision/timestamp, as shown on the diagram's "Audit Log" box.
"""

from tools import (
    retrieve_member_record,
    search_sacco_policy,
    calculate_illustrative_schedule,
    create_case_pack_draft,
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

    def record(self, tool, inputs, result):
        self.entries.append({"tool": tool, "inputs": inputs, "result": result})

    def to_list(self):
        return self.entries


class AgentTrace:
    def __init__(self, member_id):
        self.member_id = member_id
        self.steps = []
        self.status = "IN_PROGRESS"
        self.audit_log = AuditLog()

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
            "observe": {"status": status, "reason": reason,
                        "note": "Not an approval or rejection decision."},
        })

    def to_text(self):
        lines = [f"EXECUTION TRACE — member_id={self.member_id}", "=" * 60]
        for s in self.steps:
            lines.append(f"\nStep {s['step']}: {s['name']}")
            for key in ("sense", "plan", "act", "observe"):
                if s[key] is not None:
                    label = {"sense": "Sense/Context", "plan": "Plan/Decide",
                              "act": "Act/Tool", "observe": "Observe"}[key]
                    lines.append(f"  {label:<14}: {s[key]}")
        lines.append(f"\nFinal status: {self.status}")
        lines.append(f"\nAudit Log ({len(self.audit_log.entries)} tool calls):")
        for e in self.audit_log.entries:
            lines.append(f"  - {e['tool']}(inputs={e['inputs']}) -> {e['result']}")
        return "\n".join(lines)


def run_case_preparation(member_id):
    trace = AgentTrace(member_id)
    iteration = 0

    # ---- 1. Sense/Context + 2. Plan/Decide + 3. Act: retrieve_member_record
    iteration += 1
    trace.log(
        "Retrieve the case",
        sense=f"Received request to prepare a case for member_id={member_id}",
        plan="Call retrieve_member_record() to load this member's data before anything else",
        act="retrieve_member_record(member_id)",
        observe=None,
    )
    member = retrieve_member_record(member_id)
    trace.audit_log.record("retrieve_member_record", {"member_id": member_id}, member)
    trace.steps[-1]["observe"] = member

    # ---- 4. Observe -> 5. Re-plan/Stop decision
    if not member.get("record_found"):
        trace.stop("STOPPED_INCOMPLETE",
                    f"Member record not found or invalid ({member.get('error')}). "
                    "Agent stops rather than guessing member data; hand off to staff.")
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # ---- Retrieve policy evidence via search_sacco_policy()
    iteration += 1
    topics = ["eligibility", "dsr", "kyc", "guarantor"]
    trace.log(
        "Retrieve policy evidence",
        sense="Member record loaded successfully; need relevant policy evidence "
              "to ground the case before any calculations are prepared",
        plan=f"Call search_sacco_policy() for topics relevant to this case: {topics}",
        act="search_sacco_policy(topics)",
        observe=None,
    )
    policy = search_sacco_policy(topics)
    trace.audit_log.record("search_sacco_policy", {"topics": topics}, policy)
    trace.steps[-1]["observe"] = policy

    if not policy.get("evidence_found"):
        trace.replan("no policy evidence found above threshold",
                      "retry search with broader topic set")
        # Try one broader re-plan attempt before giving up
        topics_broad = ["eligibility", "dsr", "kyc", "guarantor", "general"]
        policy = search_sacco_policy(topics_broad)
        trace.audit_log.record("search_sacco_policy", {"topics": topics_broad}, policy)
        if not policy.get("evidence_found"):
            trace.stop("STOPPED_INCOMPLETE",
                        "No relevant policy evidence retrieved even after re-plan. "
                        "Agent stops rather than preparing an ungrounded brief.")
            return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # ---- Choose approved calculations via calculate_illustrative_schedule()
    iteration += 1
    applicable = []
    if member.get("requested_loan") and member.get("requested_term_months"):
        applicable.append("repayment_schedule")
    if member.get("monthly_income") is not None:
        applicable.append("debt_service_ratio")
    if member.get("savings_balance") is not None:
        applicable.append("savings_loan_limit")

    trace.log(
        "Choose approved calculations",
        sense=f"Member record contains fields relevant to: {applicable}",
        plan=f"Call calculate_illustrative_schedule() only for applicable types: {applicable}",
        act=f"calculate_illustrative_schedule(...) for each of {applicable}",
        observe=None,
    )

    calc_results = {}
    calc_failed = None

    if "repayment_schedule" in applicable:
        inputs = {
            "principal": member["requested_loan"],
            "annual_interest_rate": member["annual_interest_rate"],
            "term_months": member["requested_term_months"],
        }
        calc_results["repayment_schedule"] = calculate_illustrative_schedule(
            "repayment_schedule", inputs)
        trace.audit_log.record("calculate_illustrative_schedule",
                                {"calculation_type": "repayment_schedule", **inputs},
                                calc_results["repayment_schedule"])
        if not calc_results["repayment_schedule"]["calculation_successful"]:
            calc_failed = calc_results["repayment_schedule"]

    if not calc_failed and "debt_service_ratio" in applicable:
        inputs = {
            "net_monthly_income": member["monthly_income"],
            "existing_monthly_obligations": member["existing_monthly_obligations"],
            "proposed_monthly_installment":
                calc_results.get("repayment_schedule", {}).get("result", {}).get("monthly_payment", 0),
        }
        calc_results["debt_service_ratio"] = calculate_illustrative_schedule(
            "debt_service_ratio", inputs)
        trace.audit_log.record("calculate_illustrative_schedule",
                                {"calculation_type": "debt_service_ratio", **inputs},
                                calc_results["debt_service_ratio"])
        if not calc_results["debt_service_ratio"]["calculation_successful"]:
            calc_failed = calc_results["debt_service_ratio"]

    if not calc_failed and "savings_loan_limit" in applicable:
        inputs = {"savings_balance": member["savings_balance"], "multiplier_rate": 3}
        calc_results["savings_loan_limit"] = calculate_illustrative_schedule(
            "savings_loan_limit", inputs)
        trace.audit_log.record("calculate_illustrative_schedule",
                                {"calculation_type": "savings_loan_limit", **inputs},
                                calc_results["savings_loan_limit"])
        if not calc_results["savings_loan_limit"]["calculation_successful"]:
            calc_failed = calc_results["savings_loan_limit"]

    trace.steps[-1]["observe"] = calc_results

    if calc_failed:
        trace.stop("STOPPED_ERROR",
                    f"A required calculation failed: {calc_failed.get('error')}. "
                    "Agent stops rather than substituting an estimated figure.")
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # ---- Assess completeness ---------------------------------------------
    iteration += 1
    checklist = {
        "member_record_retrieved": True,
        "policy_evidence_retrieved": True,
        "calculations_completed": all(r["calculation_successful"] for r in calc_results.values()),
        "kyc_status": member.get("kyc_status"),
        "has_arrears": member.get("has_arrears"),
        "guarantors_declared": member.get("number_of_guarantors", 0),
    }
    is_complete = (checklist["member_record_retrieved"]
                   and checklist["policy_evidence_retrieved"]
                   and checklist["calculations_completed"])

    trace.log(
        "Assess completeness",
        sense="All tool calls so far have returned successfully",
        plan="Check whether every required input for a case pack is present",
        act="Evaluate internal completeness checklist",
        observe=checklist,
    )

    if not is_complete:
        trace.stop("STOPPED_INCOMPLETE", f"Required inputs incomplete: {checklist}")
        return trace

    if iteration >= MAX_ITERATIONS:
        trace.stop("STOPPED_ITERATION_LIMIT", "Reached maximum iterations.")
        return trace

    # ---- Act: create_case_pack_draft() ------------------------------------
    iteration += 1
    draft_result = create_case_pack_draft(
        member_id=member["member_id"],
        policy_evidence=policy["evidence"],
        calculations=calc_results,
    )
    trace.audit_log.record("create_case_pack_draft",
                            {"member_id": member["member_id"]}, draft_result)
    trace.log(
        "Prepare draft case brief",
        sense="All required data, policy evidence, and calculations are present",
        plan="Call create_case_pack_draft() to assemble the final case pack",
        act="create_case_pack_draft(...)",
        observe=draft_result,
    )

    if draft_result.get("status") != "DRAFT_READY_FOR_HUMAN_REVIEW":
        trace.stop("STOPPED_INCOMPLETE",
                    f"Case pack assembly failed: {draft_result.get('error')}")
        return trace

    # ---- 6. Stop: case pack complete, ready for review --------------------
    trace.status = "READY_FOR_REVIEW"
    trace.steps.append({
        "step": len(trace.steps) + 1,
        "name": "STOP (safe hand-off)",
        "sense": "Case pack complete",
        "plan": "Hand off to a human SACCO officer; take no further autonomous action",
        "act": None,
        "observe": {
            "status": "READY_FOR_REVIEW",
            "case_pack_id": draft_result["case_pack_id"],
            "note": "Not an approval or rejection decision.",
        },
    })

    return trace
