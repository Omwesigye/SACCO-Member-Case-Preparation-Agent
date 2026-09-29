"""
Application Orchestration Layer - SACCO Member-Case Preparation Agent

Enforces application security, authorization, parameter validation, failure
handling, and the Human Approval Gate between the AI agent and underlying tools.

Security Principle:
"The model may request a tool operation, but the application decides whether
the operation is allowed." (Test_Authorisation_and_FailureHandling.md, Section 11)

Governed Tools:
1. retrieve_member_record (Tools/member_record_tool.py)
2. run_financial_calculation (Tools/repayment_calculator_tool.py)
3. create_case_draft (Draft Case Preparation Record)
"""

import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path so relative imports work seamlessly
tools_dir = Path(__file__).resolve().parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from member_record_tool import retrieve_member_record
from repayment_calculator_tool import run_calculation


@dataclass
class UserContext:
    """Represents the authenticated user interacting with the orchestration layer."""
    user_id: str
    role: str
    is_authenticated: bool = True
    session_id: Optional[str] = None


# Allowed roles for loan case preparation
AUTHORIZED_ROLES = {"Loan Officer", "Senior Loan Officer", "Credit Admin"}

# Strictly prohibited autonomous actions (High-Impact actions requiring Human Approval Gate)
FORBIDDEN_OPERATIONS = {
    "approveLoan",
    "approveloan",
    "approve_loan",
    "rejectLoan",
    "reject_loan",
    "disburseLoan",
    "disburse_funds",
    "modifyAccount",
    "modify_member_account",
    "executeTransaction",
    "execute_financial_transaction",
    "creditScoring",
    "perform_credit_scoring"
}

# Required schema fields for retrieve_member_record output validation
MEMBER_RECORD_REQUIRED_FIELDS = {
    "member_id",
    "full_name",
    "membership_months",
    "monthly_income",
    "monthly_savings",
    "savings_balance",
    "existing_monthly_obligations",
    "kyc_status",
    "has_arrears",
    "number_of_guarantors",
    "data_type",
    "record_found"
}


class ApplicationOrchestrator:
    """
    Central Orchestration Layer that gates all tool invocations from the AI agent.
    """

    def __init__(self):
        self._draft_store: Dict[str, Dict[str, Any]] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def _log_event(self, event_type: str, user: Optional[UserContext], details: Dict[str, Any]) -> None:
        """Maintains an auditable log of all attempted operations."""
        self._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user.user_id if user else None,
            "role": user.role if user else None,
            "details": details
        })

    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user: Optional[UserContext],
        simulate_failure: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches and executes a tool call under strict authorization and validation.

        Args:
            tool_name: The name of the tool requested.
            parameters: The input payload.
            user: The authenticated UserContext.
            simulate_failure: Optional string to simulate failures (e.g. 'service_unavailable', 'timeout').

        Returns:
            Structured standard envelope:
            {
                "status": "SUCCESS" | "UNAUTHORIZED" | "AUTHENTICATION_REQUIRED" |
                          "FORBIDDEN_OPERATION" | "INVALID_PARAMETERS" |
                          "SERVICE_UNAVAILABLE" | "INVALID_TOOL_RESPONSE" |
                          "TOOL_TIMEOUT" | "HUMAN_APPROVAL_REQUIRED",
                "tool_name": str,
                "data": Optional[Dict[str, Any]],
                "error": Optional[str],
                "message": Optional[str]
            }
        """
        # --- 1. Check Authentication (AUTH-03) ---
        if not user or not user.is_authenticated:
            self._log_event("AUTH_FAILED", user, {"tool": tool_name, "reason": "missing_or_invalid_auth"})
            return {
                "status": "AUTHENTICATION_REQUIRED",
                "tool_name": tool_name,
                "data": None,
                "error": "authentication_required",
                "message": "Authentication required. A valid session must be established before tools can be invoked."
            }

        # --- 2. Intercept High-Impact / Forbidden Actions (AUTH-04 & HUMAN-01) ---
        if tool_name in FORBIDDEN_OPERATIONS:
            self._log_event("FORBIDDEN_ATTEMPT", user, {"tool": tool_name})
            return {
                "status": "FORBIDDEN_OPERATION",
                "tool_name": tool_name,
                "data": None,
                "error": "human_approval_required",
                "message": (
                    f"Operation '{tool_name}' is outside the agent's permitted scope. "
                    "High-impact credit decisions and financial transactions require explicit "
                    "authorization by a designated SACCO human decision maker."
                )
            }

        # --- 3. Check Role Authorization (AUTH-01 & AUTH-02) ---
        if user.role not in AUTHORIZED_ROLES:
            self._log_event("UNAUTHORIZED_ROLE", user, {"tool": tool_name, "role": user.role})
            return {
                "status": "UNAUTHORIZED",
                "tool_name": tool_name,
                "data": None,
                "error": "unauthorized_role",
                "message": f"The requested operation is not authorized for user role '{user.role}'."
            }

        # --- 4. Dispatch by Tool ---
        if tool_name == "retrieve_member_record":
            return self._handle_retrieve_member_record(parameters, user, simulate_failure)

        elif tool_name == "run_financial_calculation":
            return self._handle_run_financial_calculation(parameters, user, simulate_failure)

        elif tool_name == "create_case_draft":
            return self._handle_create_case_draft(parameters, user, simulate_failure)

        else:
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": tool_name,
                "data": None,
                "error": "unsupported_tool",
                "message": f"Tool '{tool_name}' is not recognized in the approved tool catalogue."
            }

    # --------------------------------------------------------------------------
    # Tool Handler: retrieve_member_record
    # --------------------------------------------------------------------------
    def _handle_retrieve_member_record(
        self,
        parameters: Dict[str, Any],
        user: UserContext,
        simulate_failure: Optional[str]
    ) -> Dict[str, Any]:
        """Validates parameters, executes member record retrieval, and validates response schema."""
        # Parameter validation: PARAM-01 & PARAM-02
        member_id = parameters.get("member_id")
        app_id_required = parameters.get("require_application_id", False)
        application_id = parameters.get("application_id")

        if member_id is None or member_id == "":
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "missing_member_id",
                "message": "member_id is required before member case data can be retrieved."
            }

        if app_id_required and not application_id:
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "missing_application_id",
                "message": "Application ID is required before the member case can be retrieved."
            }

        if application_id and not re.match(r"^APP-[0-9]{4}$", str(application_id)):
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "invalid_application_id_format",
                "message": f"Application ID '{application_id}' does not match required format '^APP-[0-9]{{4}}$'."
            }

        # Simulated timeouts (FAIL-05)
        if simulate_failure == "timeout":
            return {
                "status": "TOOL_TIMEOUT",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "tool_timeout",
                "message": "The member record service timed out after 5000ms. No data retrieved."
            }

        # Simulated service unavailable (FAIL-01)
        if simulate_failure == "service_unavailable":
            return {
                "status": "SERVICE_UNAVAILABLE",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "data_service_unavailable",
                "message": "The member case data service is currently unavailable. Please try again later."
            }

        # Execute underlying tool
        tool_output = retrieve_member_record(member_id, simulate_failure=simulate_failure)

        # Check if underlying tool encountered format or not found issues
        if not tool_output.get("record_found"):
            err_code = tool_output.get("error")
            if err_code == "invalid_member_id_format":
                return {
                    "status": "INVALID_PARAMETERS",
                    "tool_name": "retrieve_member_record",
                    "data": tool_output,
                    "error": err_code,
                    "message": tool_output.get("message", "Invalid member identifier format.")
                }
            elif err_code == "data_source_unavailable":
                return {
                    "status": "SERVICE_UNAVAILABLE",
                    "tool_name": "retrieve_member_record",
                    "data": None,
                    "error": err_code,
                    "message": "Underlying synthetic dataset is currently unavailable."
                }
            elif err_code == "tool_timeout":
                return {
                    "status": "TOOL_TIMEOUT",
                    "tool_name": "retrieve_member_record",
                    "data": None,
                    "error": err_code,
                    "message": "The member record service timed out."
                }

        # Schema Validation: Detect Malformed (FAIL-03) or Partial (FAIL-04) responses
        if not isinstance(tool_output, dict):
            return {
                "status": "INVALID_TOOL_RESPONSE",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "malformed_response",
                "message": "Tool returned non-dictionary response."
            }

        missing_fields = MEMBER_RECORD_REQUIRED_FIELDS - set(tool_output.keys())
        if missing_fields:
            return {
                "status": "INVALID_TOOL_RESPONSE",
                "tool_name": "retrieve_member_record",
                "data": None,
                "error": "incomplete_response",
                "message": f"Tool response is missing required fields: {sorted(list(missing_fields))}"
            }

        # If well-formed and record not found in database
        if not tool_output.get("record_found"):
            return {
                "status": "SUCCESS",
                "tool_name": "retrieve_member_record",
                "data": tool_output,
                "error": tool_output.get("error"),
                "message": tool_output.get("message", "Member record not found.")
            }

        # Attach application_id if supplied
        if application_id:
            tool_output["application_id"] = application_id

        self._log_event("TOOL_EXECUTION_SUCCESS", user, {"tool": "retrieve_member_record", "member_id": member_id})
        return {
            "status": "SUCCESS",
            "tool_name": "retrieve_member_record",
            "data": tool_output,
            "error": None,
            "message": "Member record successfully retrieved from authorized synthetic store."
        }

    # --------------------------------------------------------------------------
    # Tool Handler: run_financial_calculation
    # --------------------------------------------------------------------------
    def _handle_run_financial_calculation(
        self,
        parameters: Dict[str, Any],
        user: UserContext,
        simulate_failure: Optional[str]
    ) -> Dict[str, Any]:
        """Dispatches deterministic financial arithmetic to the calculation engine."""
        if simulate_failure == "service_unavailable":
            return {
                "status": "SERVICE_UNAVAILABLE",
                "tool_name": "run_financial_calculation",
                "data": None,
                "error": "calculation_service_unavailable",
                "message": "The calculation service is currently unreachable."
            }

        calc_type = parameters.get("calculation_type")
        inputs = parameters.get("inputs")

        if not calc_type or not inputs:
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "run_financial_calculation",
                "data": None,
                "error": "missing_calculation_type_or_inputs",
                "message": "calculation_type and inputs dictionary are required."
            }

        # Invoke deterministic calculation engine
        calc_response = run_calculation(parameters)

        if not calc_response.get("calculation_successful", False):
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "run_financial_calculation",
                "data": calc_response,
                "error": calc_response.get("error", "calculation_failed"),
                "message": f"Calculation failed: {calc_response.get('error')}"
            }

        self._log_event("TOOL_EXECUTION_SUCCESS", user, {"tool": "run_financial_calculation", "type": calc_type})
        return {
            "status": "SUCCESS",
            "tool_name": "run_financial_calculation",
            "data": calc_response,
            "error": None,
            "message": "Deterministic financial calculation completed successfully."
        }

    # --------------------------------------------------------------------------
    # Tool Handler: create_case_draft (DRAFT-01)
    # --------------------------------------------------------------------------
    def _handle_create_case_draft(
        self,
        parameters: Dict[str, Any],
        user: UserContext,
        simulate_failure: Optional[str]
    ) -> Dict[str, Any]:
        """Creates a preliminary draft case preparation record requiring human review."""
        if simulate_failure == "service_unavailable":
            return {
                "status": "SERVICE_UNAVAILABLE",
                "tool_name": "create_case_draft",
                "data": None,
                "error": "draft_service_unavailable",
                "message": "Case draft creation service is currently unavailable. No draft was created."
            }

        member_id = parameters.get("member_id")
        if not member_id:
            return {
                "status": "INVALID_PARAMETERS",
                "tool_name": "create_case_draft",
                "data": None,
                "error": "missing_member_id",
                "message": "member_id is required to create a case draft."
            }

        draft_id = f"DRAFT-{datetime.utcnow().year}-{len(self._draft_store) + 1:03d}"
        draft_record = {
            "draft_id": draft_id,
            "member_id": member_id,
            "created_by": user.user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "CREATED_DRAFT",
            "requires_human_approval": True,
            "content": parameters.get("draft_summary", {})
        }
        self._draft_store[draft_id] = draft_record

        self._log_event("DRAFT_CREATED", user, {"draft_id": draft_id, "member_id": member_id})
        return {
            "status": "SUCCESS",
            "tool_name": "create_case_draft",
            "data": {
                "status": "CREATED",
                "draftId": draft_id,
                "message": "Case preparation draft created successfully. Record remains a draft and requires human review."
            },
            "error": None,
            "message": "Case preparation draft created successfully."
        }
