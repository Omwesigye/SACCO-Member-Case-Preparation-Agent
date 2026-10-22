"""
SACCO Agent Observability and Tracing Module

This module adds structured JSON logging and trace evidence to the
SACCO Member-Case Preparation Agent.

It records:
- A unique trace ID for each agent run
- The user request and user role
- Workflow state transitions
- Retrieved policy sources and policy version
- Tool calls, inputs, outputs, errors, and latency
- Agent decisions, stop reason, and final outcome
- Human handover or approval events

Run:
    python observability_tracing.py

The module writes:
    output/agent_traces.jsonl
    output/agent_events.jsonl
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


TRACE_FILE = Path("output/agent_traces.jsonl")
EVENT_FILE = Path("output/agent_events.jsonl")


def utc_now() -> str:
    """
    Return the current UTC time in ISO 8601 format.
    """

    return datetime.now(timezone.utc).isoformat()


def ensure_output_files() -> None:
    """
    Create the output folder and evidence files if they do not exist.
    """

    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not TRACE_FILE.exists():
        TRACE_FILE.touch()

    if not EVENT_FILE.exists():
        EVENT_FILE.touch()


def new_trace_id() -> str:
    """
    Create a unique trace ID for one complete agent run.
    """

    return f"TRACE-{uuid.uuid4().hex[:12].upper()}"


def new_event_id() -> str:
    """
    Create a unique event ID for one workflow event.
    """

    return f"EVENT-{uuid.uuid4().hex[:12].upper()}"


def write_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    """
    Append one JSON record to a JSON Lines evidence file.
    """

    ensure_output_files()

    with path.open("a", encoding="utf-8") as evidence_file:
        evidence_file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )


class AgentTrace:
    """
    Represents one complete SACCO agent workflow run.

    A trace contains the user request, workflow state, policy evidence,
    tool calls, latency, errors, decisions, and final outcome.
    """

    def __init__(
        self,
        case_id: str,
        user_id: str,
        user_role: str,
        loan_product: str
    ) -> None:

        self.trace_id = new_trace_id()
        self.case_id = case_id
        self.user_id = user_id
        self.user_role = user_role
        self.loan_product = loan_product

        self.started_at = utc_now()
        self.started_time = time.perf_counter()

        self.current_state = "RECEIVED"
        self.iterations = 0
        self.tool_calls = 0

        self.policy_sources = []
        self.tool_events = []
        self.state_history = []

        self.final_outcome = None
        self.stop_reason = None
        self.safety_violation = False

        self.record_state(
            "RECEIVED",
            "Agent run started"
        )

    def elapsed_seconds(self) -> float:
        """
        Return the elapsed workflow time in seconds.
        """

        elapsed = time.perf_counter() - self.started_time

        return round(elapsed, 3)

    def record_state(self, state, reason):
        """
        Record a workflow state transition.
        """

        self.current_state = state

        event = {
            "event_id": new_event_id(),
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "event_type": "STATE_TRANSITION",
            "state": state,
            "reason": reason,
            "iteration": self.iterations,
            "timestamp": utc_now()
        }

        self.state_history.append(event)

        write_jsonl(EVENT_FILE, event)

    def record_policy_source(
        self,
        document_title,
        policy_version,
        section,
        page,
        effective_date
    ):
        """
        Record one approved SACCO policy source used by the agent.
        """

        policy_source = {
            "document_title": document_title,
            "policy_version": policy_version,
            "section": section,
            "page": page,
            "effective_date": effective_date
        }

        self.policy_sources.append(policy_source)

        event = {
            "event_id": new_event_id(),
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "event_type": "POLICY_RETRIEVAL",
            "policy_source": policy_source,
            "timestamp": utc_now()
        }

        write_jsonl(EVENT_FILE, event)

    def record_tool_call(
        self,
        tool_name,
        tool_input,
        tool_output,
        status,
        error_code=None,
        authorized=True
    ):
        """
        Record one tool call, its result, authorization, and error.
        """

        self.tool_calls += 1

        event = {
            "event_id": new_event_id(),
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "event_type": "TOOL_CALL",
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "status": status,
            "authorized": authorized,
            "error_code": error_code,
            "tool_call_number": self.tool_calls,
            "iteration": self.iterations,
            "timestamp": utc_now()
        }

        self.tool_events.append(event)

        write_jsonl(EVENT_FILE, event)

        return event

    def record_safety_event(
        self,
        event_name,
        reason,
        blocked=True
    ):
        """
        Record a guardrail, authorization, or prompt-injection event.
        """

        if blocked:
            self.safety_violation = True

        event = {
            "event_id": new_event_id(),
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "event_type": "SAFETY_EVENT",
            "event_name": event_name,
            "reason": reason,
            "blocked": blocked,
            "timestamp": utc_now()
        }

        write_jsonl(EVENT_FILE, event)

    def complete(self, final_outcome, stop_reason):
        """
        Complete the trace and write the final trace summary.
        """

        self.final_outcome = final_outcome
        self.stop_reason = stop_reason

        self.record_state(
            final_outcome,
            stop_reason
        )

        trace_record = {
            "trace_id": self.trace_id,
            "case_id": self.case_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "loan_product": self.loan_product,
            "started_at": self.started_at,
            "completed_at": utc_now(),
            "total_latency_seconds": self.elapsed_seconds(),
            "iterations": self.iterations,
            "total_tool_calls": self.tool_calls,
            "workflow_states": self.state_history,
            "policy_sources": self.policy_sources,
            "tool_events": self.tool_events,
            "final_outcome": self.final_outcome,
            "stop_reason": self.stop_reason,
            "safety_violation": self.safety_violation
        }

        write_jsonl(TRACE_FILE, trace_record)

        return trace_record


class TracedAgentWorkflow:
    """
    A simple bounded SACCO agent workflow with observability.

    It demonstrates:
    - Sense/Context
    - Plan/Decide
    - Act/Tool
    - Observe
    - Stop/Handover
    """

    APPROVED_TOOLS = {
        "get_member_record",
        "get_member_case",
        "search_sacco_policy",
        "calculate_repayment_schedule",
        "calculate_dsr",
        "calculate_savings_based_limit",
        "calculate_security_coverage",
        "calculate_guarantor_coverage",
        "create_draft_case_pack"
    }

    MAX_ITERATIONS = 6
    MAX_TOOL_CALLS = 10

    def __init__(self, trace):
        self.trace = trace

    def is_tool_allowed(self, tool_name):
        """
        Check whether a tool is on the approved allow-list.
        """

        return tool_name in self.APPROVED_TOOLS

    def can_continue(self):
        """
        Check whether the agent remains within iteration and call limits.
        """

        within_iteration_limit = (
            self.trace.iterations < self.MAX_ITERATIONS
        )

        within_tool_limit = (
            self.trace.tool_calls < self.MAX_TOOL_CALLS
        )

        return within_iteration_limit and within_tool_limit

    def run(self, case_data):
        """
        Run the simplified SACCO case-preparation workflow.
        """

        self.trace.iterations += 1

        self.trace.record_state(
            "CONTEXT_COLLECTION",
            "Retrieving member, case, and policy context"
        )

        # Step 1: Retrieve member record.
        if not self.can_continue():
            return self.handover(
                "Maximum workflow limit reached"
            )

        member_result = self.call_tool(
            "get_member_record",
            {
                "member_id": case_data.get("member_id")
            },
            {
                "status": "success",
                "eligible_savings_ugx": 3500000
            }
        )

        if member_result["tool_output"]["status"] != "success":
            return self.handover(
                "Member record unavailable"
            )

        # Step 2: Retrieve policy evidence.
        if not self.can_continue():
            return self.handover(
                "Maximum workflow limit reached"
            )

        policy_result = self.call_tool(
            "search_sacco_policy",
            {
                "loan_product": self.trace.loan_product
            },
            {
                "status": "success",
                "policy_version": "v3.0",
                "section": "4.2 Development Loans"
            }
        )

        if policy_result["tool_output"]["status"] != "success":
            return self.handover(
                "Approved policy evidence unavailable"
            )

        self.trace.record_policy_source(
            document_title="SACCO Credit Policy",
            policy_version=(
                policy_result["tool_output"]["policy_version"]
            ),
            section=(
                policy_result["tool_output"]["section"]
            ),
            page=18,
            effective_date="2026-02-01"
        )

        # Step 3: Calculate repayment schedule.
        if not self.can_continue():
            return self.handover(
                "Maximum workflow limit reached"
            )

        schedule_result = self.call_tool(
            "calculate_repayment_schedule",
            {
                "loan_amount_ugx": case_data.get(
                    "requested_loan_amount_ugx"
                ),
                "annual_interest_rate_percent": 12,
                "repayment_period_months": case_data.get(
                    "requested_tenor_months"
                ),
                "first_repayment_date": case_data.get(
                    "first_repayment_date"
                )
            },
            {
                "status": "success",
                "monthly_installment_ugx": 444244,
                "total_installments_ugx": 5330933
            }
        )

        if schedule_result["tool_output"]["status"] != "success":
            return self.handover(
                "Repayment calculation failed"
            )

        # Step 4: Check savings-based limit.
        if not self.can_continue():
            return self.handover(
                "Maximum workflow limit reached"
            )

        savings_result = self.call_tool(
            "calculate_savings_based_limit",
            {
                "eligible_savings_ugx": 3500000,
                "savings_multiple": 3,
                "requested_loan_amount_ugx": case_data.get(
                    "requested_loan_amount_ugx"
                )
            },
            {
                "status": "success",
                "available_loan_ceiling_ugx": 10500000,
                "passes_limit": True
            }
        )

        if not savings_result["tool_output"]["passes_limit"]:
            return self.handover(
                "Requested loan amount exceeds savings-based limit"
            )

        # Step 5: Create draft case pack.
        if not self.can_continue():
            return self.handover(
                "Maximum workflow limit reached"
            )

        draft_result = self.call_tool(
            "create_draft_case_pack",
            {
                "case_id": self.trace.case_id,
                "prepared_by": self.trace.user_id
            },
            {
                "status": "success",
                "draft_case_pack_id": "DRAFT-CP-2026-101",
                "case_pack_status": "Draft"
            }
        )

        if draft_result["tool_output"]["status"] != "success":
            return self.handover(
                "Draft case pack could not be created"
            )

        return self.complete_for_review(
            draft_result["tool_output"]
        )

    def call_tool(
        self,
        tool_name,
        tool_input,
        simulated_output
    ):
        """
        Validate, authorize, call, observe, and log one tool.
        """

        if not self.is_tool_allowed(tool_name):
            self.trace.record_safety_event(
                "UNAUTHORIZED_TOOL_REQUEST",
                f"Tool {tool_name} is not on the approved allow-list"
            )

            return self.trace.record_tool_call(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=None,
                status="error",
                error_code="UNAUTHORIZED_TOOL_REQUEST",
                authorized=False
            )

        if not self.can_continue():
            self.trace.record_safety_event(
                "WORKFLOW_LIMIT_REACHED",
                "Maximum iterations or tool calls reached"
            )

            return self.trace.record_tool_call(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=None,
                status="error",
                error_code="WORKFLOW_LIMIT_REACHED",
                authorized=True
            )

        # In a real system, this is where the actual tool is called.
        return self.trace.record_tool_call(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=simulated_output,
            status="success",
            authorized=True
        )

    def complete_for_review(self, draft_result):
        """
        Complete the workflow with a successful staff-review handover.
        """

        response = {
            "status": "success",
            "trace_id": self.trace.trace_id,
            "case_id": self.trace.case_id,
            "draft_case_pack_id": draft_result[
                "draft_case_pack_id"
            ],
            "final_outcome": "AWAITING_LOAN_OFFICER_REVIEW",
            "message": (
                "Draft case brief prepared. It is awaiting loan officer "
                "review and is not a loan approval."
            )
        }

        self.trace.complete(
            final_outcome="AWAITING_LOAN_OFFICER_REVIEW",
            stop_reason=(
                "Draft case brief prepared for staff review"
            )
        )

        return response

    def handover(self, reason):
        """
        Stop safely and hand the case to a human loan officer.
        """

        response = {
            "status": "handover_required",
            "trace_id": self.trace.trace_id,
            "case_id": self.trace.case_id,
            "final_outcome": "HANDOFF_REQUIRED",
            "stop_reason": reason,
            "message": (
                "The agent stopped safely and requires loan officer action."
            )
        }

        self.trace.complete(
            final_outcome="HANDOFF_REQUIRED",
            stop_reason=reason
        )

        return response


def demonstrate_successful_trace():
    """
    Create evidence for a successful case-preparation run.
    """

    trace = AgentTrace(
        case_id="CASE-2026-001",
        user_id="loan.officer@sacco.local",
        user_role="Loan Officer",
        loan_product="Development Loan"
    )

    workflow = TracedAgentWorkflow(trace)

    case_data = {
        "member_id": "MEM-2026-001",
        "requested_loan_amount_ugx": 5000000,
        "requested_tenor_months": 12,
        "first_repayment_date": "2026-10-31"
    }

    return workflow.run(case_data)


def demonstrate_unauthorized_tool_trace():
    """
    Create evidence for an unauthorized tool-call failure.
    """

    trace = AgentTrace(
        case_id="CASE-2026-002",
        user_id="loan.officer@sacco.local",
        user_role="Loan Officer",
        loan_product="Development Loan"
    )

    workflow = TracedAgentWorkflow(trace)

    workflow.call_tool(
        "approve_loan",
        {
            "case_id": "CASE-2026-002"
        },
        {
            "status": "success"
        }
    )

    return workflow.handover(
        "Unauthorized tool request blocked"
    )


def demonstrate_missing_policy_trace():
    """
    Create evidence for a missing-policy handover and safe stop.
    """

    trace = AgentTrace(
        case_id="CASE-2026-003",
        user_id="loan.officer@sacco.local",
        user_role="Loan Officer",
        loan_product="Unknown Loan Product"
    )

    workflow = TracedAgentWorkflow(trace)

    workflow.call_tool(
        "get_member_record",
        {
            "member_id": "MEM-2026-003"
        },
        {
            "status": "success"
        }
    )

    workflow.call_tool(
        "search_sacco_policy",
        {
            "loan_product": "Unknown Loan Product"
        },
        {
            "status": "error",
            "error_code": "POLICY_NOT_FOUND"
        }
    )

    return workflow.handover(
        "Approved policy evidence unavailable"
    )


if __name__ == "__main__":
    ensure_output_files()

    successful_trace = demonstrate_successful_trace()
    unauthorized_trace = demonstrate_unauthorized_tool_trace()
    missing_policy_trace = demonstrate_missing_policy_trace()

    print("Observability demonstration completed.")
    print(
        f"Successful trace: {successful_trace['trace_id']}"
    )
    print(
        f"Unauthorized trace: {unauthorized_trace['trace_id']}"
    )
    print(
        f"Missing-policy trace: {missing_policy_trace['trace_id']}"
    )
    print(f"Trace summary file: {TRACE_FILE}")
    print(f"Event evidence file: {EVENT_FILE}")