"""
Test and Demonstration Suite: Tool Authorization, Orchestration, and Failure Handling

Executes all 14 test cases defined in Tools/Test_Authorisation_and_FailureHandling.md
plus deterministic calculations from Tools/tool-catalogue.md. Demonstrates that
authorization, validation, and safety gates are strictly enforced at the
application orchestration layer outside the AI model.

Run with pytest:
    pytest tests/test_tools_orchestration.py -v

Run standalone with detailed demonstration report:
    python tests/test_tools_orchestration.py
"""

import sys
from pathlib import Path
import pytest

# Ensure Tools directory is on the path
repo_root = Path(__file__).resolve().parents[1]
tools_dir = repo_root / "Tools"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from orchestration_layer import ApplicationOrchestrator, UserContext


@pytest.fixture
def orchestrator():
    return ApplicationOrchestrator()


@pytest.fixture
def loan_officer():
    return UserContext(user_id="LO-001", role="Loan Officer", is_authenticated=True)


@pytest.fixture
def unauthorized_user():
    return UserContext(user_id="MEMBER-99", role="Member", is_authenticated=True)


@pytest.fixture
def unauthenticated_user():
    return UserContext(user_id="ANON", role="Guest", is_authenticated=False)


# ==============================================================================
# 1. Authorization Tests (AUTH-01 to AUTH-04, HUMAN-01)
# ==============================================================================

def test_auth_01_authorized_retrieval(orchestrator, loan_officer):
    """AUTH-01: Authorized Loan Officer retrieves member case information."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001", "application_id": "APP-1001"},
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    assert response["data"]["record_found"] is True
    assert response["data"]["member_id"] == "SACCO-M-001"
    assert response["data"]["data_type"] == "synthetic"


def test_auth_02_unauthorized_role(orchestrator, unauthorized_user):
    """AUTH-02: Unauthorized role attempts member data retrieval."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=unauthorized_user
    )
    assert response["status"] == "UNAUTHORIZED"
    assert response["data"] is None
    assert "not authorized" in response["message"].lower()


def test_auth_03_unauthenticated_request(orchestrator, unauthenticated_user):
    """AUTH-03: Unauthenticated tool request rejected."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=unauthenticated_user
    )
    assert response["status"] == "AUTHENTICATION_REQUIRED"
    assert response["data"] is None


def test_auth_04_forbidden_high_impact_action(orchestrator, loan_officer):
    """AUTH-04: Prohibited high-impact operation (e.g. approveLoan) is blocked."""
    response = orchestrator.execute_tool(
        tool_name="approveLoan",
        parameters={"application_id": "APP-1001"},
        user=loan_officer
    )
    assert response["status"] == "FORBIDDEN_OPERATION"
    assert response["data"] is None
    assert "human" in response["message"].lower()


def test_human_01_human_approval_gate(orchestrator, loan_officer):
    """HUMAN-01: Loan disbursement / financial transaction blocked by Human Approval Gate."""
    for action in ["disburseLoan", "modifyAccount", "creditScoring"]:
        response = orchestrator.execute_tool(
            tool_name=action,
            parameters={"account_id": "ACC-1234"},
            user=loan_officer
        )
        assert response["status"] == "FORBIDDEN_OPERATION"


# ==============================================================================
# 2. Missing & Invalid Parameter Tests (PARAM-01 to PARAM-03)
# ==============================================================================

def test_param_01_missing_member_id(orchestrator, loan_officer):
    """PARAM-01: Incomplete request with missing member ID is rejected."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"application_id": "APP-1001"},
        user=loan_officer
    )
    assert response["status"] == "INVALID_PARAMETERS"
    assert "member_id" in response["error"]


def test_param_02_missing_application_id_when_required(orchestrator, loan_officer):
    """PARAM-02: Missing application ID when required by workflow is rejected."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001", "require_application_id": True},
        user=loan_officer
    )
    assert response["status"] == "INVALID_PARAMETERS"
    assert "missing_application_id" in response["error"]


def test_param_03_invalid_parameter_format(orchestrator, loan_officer):
    """PARAM-03: Invalid identifier format fails schema validation."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "INVALID"},
        user=loan_officer
    )
    assert response["status"] == "INVALID_PARAMETERS"
    assert "invalid_member_id_format" in response["error"]


# ==============================================================================
# 3. Service Failure & Availability Tests (FAIL-01 to FAIL-05)
# ==============================================================================

def test_fail_01_member_data_service_unavailable(orchestrator, loan_officer):
    """FAIL-01: Member data service unavailable returns controlled error, no fabrication."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=loan_officer,
        simulate_failure="service_unavailable"
    )
    assert response["status"] == "SERVICE_UNAVAILABLE"
    assert response["data"] is None


def test_fail_02_draft_service_unavailable(orchestrator, loan_officer):
    """FAIL-02: Case draft service unavailable returns controlled error."""
    response = orchestrator.execute_tool(
        tool_name="create_case_draft",
        parameters={"member_id": "SACCO-M-001"},
        user=loan_officer,
        simulate_failure="service_unavailable"
    )
    assert response["status"] == "SERVICE_UNAVAILABLE"
    assert response["data"] is None


def test_fail_03_malformed_tool_response(orchestrator, loan_officer):
    """FAIL-03: Malformed tool response detected and rejected by response validator."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=loan_officer,
        simulate_failure="malformed_response"
    )
    assert response["status"] == "INVALID_TOOL_RESPONSE"
    assert "missing required fields" in response["message"]


def test_fail_04_incomplete_tool_response(orchestrator, loan_officer):
    """FAIL-04: Partial response omitting required schema fields is rejected."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=loan_officer,
        simulate_failure="incomplete_response"
    )
    assert response["status"] == "INVALID_TOOL_RESPONSE"
    assert "missing required fields" in response["message"]


def test_fail_05_tool_timeout(orchestrator, loan_officer):
    """FAIL-05: Tool timeout handled safely without assuming data."""
    response = orchestrator.execute_tool(
        tool_name="retrieve_member_record",
        parameters={"member_id": "SACCO-M-001"},
        user=loan_officer,
        simulate_failure="timeout"
    )
    assert response["status"] == "TOOL_TIMEOUT"
    assert response["data"] is None


# ==============================================================================
# 4. Draft Creation Authorization Test (DRAFT-01)
# ==============================================================================

def test_draft_01_authorized_draft_creation(orchestrator, loan_officer):
    """DRAFT-01: Loan Officer creates a preliminary draft case record."""
    response = orchestrator.execute_tool(
        tool_name="create_case_draft",
        parameters={
            "member_id": "SACCO-M-001",
            "draft_summary": {"notes": "Draft for review", "requested_amount": 5000000}
        },
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    assert response["data"]["status"] == "CREATED"
    assert response["data"]["draftId"].startswith("DRAFT-")


# ==============================================================================
# 5. Deterministic Financial Calculator Tool Tests (CALC-01 to CALC-04)
# ==============================================================================

def test_calc_01_repayment_schedule(orchestrator, loan_officer):
    """CALC-01: Reducing-balance repayment schedule calculation."""
    response = orchestrator.execute_tool(
        tool_name="run_financial_calculation",
        parameters={
            "calculation_type": "repayment_schedule",
            "inputs": {
                "principal": 5000000,
                "annual_interest_rate": 18,
                "term_months": 12
            }
        },
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    res = response["data"]["result"]
    assert res["monthly_payment"] > 0
    assert res["total_interest"] > 0
    assert res["total_repayment"] > 5000000


def test_calc_02_debt_service_ratio(orchestrator, loan_officer):
    """CALC-02: Debt Service Ratio (DSR) evaluation."""
    response = orchestrator.execute_tool(
        tool_name="run_financial_calculation",
        parameters={
            "calculation_type": "debt_service_ratio",
            "inputs": {
                "net_monthly_income": 1500000,
                "existing_monthly_obligations": 200000,
                "proposed_monthly_installment": 300000
            }
        },
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    res = response["data"]["result"]
    assert "dsr_percentage" in res
    assert res["within_policy_limit"] is True  # (200k + 300k)/1.5M = 33.3% <= 50%


def test_calc_03_savings_loan_limit(orchestrator, loan_officer):
    """CALC-03: Savings multiplier loan limit."""
    response = orchestrator.execute_tool(
        tool_name="run_financial_calculation",
        parameters={
            "calculation_type": "savings_loan_limit",
            "inputs": {
                "savings_balance": 2000000,
                "multiplier_rate": 3
            }
        },
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    res = response["data"]["result"]
    assert res["max_eligible_loan_amount"] == 6000000


def test_calc_04_security_coverage(orchestrator, loan_officer):
    """CALC-04: Security/collateral coverage percentage."""
    response = orchestrator.execute_tool(
        tool_name="run_financial_calculation",
        parameters={
            "calculation_type": "security_coverage",
            "inputs": {
                "loan_principal": 10000000,
                "total_pledged_security": 12000000
            }
        },
        user=loan_officer
    )
    assert response["status"] == "SUCCESS"
    res = response["data"]["result"]
    assert res["coverage_percentage"] == 120.0
    assert res["meets_minimum_coverage"] is True


# ==============================================================================
# Standalone Demonstration Runner
# ==============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("  SACCO AGENT TOOL ORCHESTRATION & AUTHORIZATION DEMONSTRATION")
    print("=" * 75)

    orch = ApplicationOrchestrator()
    lo = UserContext(user_id="LO-001", role="Loan Officer")
    unauth = UserContext(user_id="MEMBER-99", role="Member")
    anon = UserContext(user_id="ANON", role="Guest", is_authenticated=False)

    test_runs = [
        ("AUTH-01", "Authorized Loan Officer retrieves case", "retrieve_member_record", {"member_id": "SACCO-M-001"}, lo, None, "SUCCESS"),
        ("AUTH-02", "Unauthorized role retrieves case", "retrieve_member_record", {"member_id": "SACCO-M-001"}, unauth, None, "UNAUTHORIZED"),
        ("AUTH-03", "Unauthenticated tool request", "retrieve_member_record", {"member_id": "SACCO-M-001"}, anon, None, "AUTHENTICATION_REQUIRED"),
        ("AUTH-04", "Agent attempts prohibited approval", "approveLoan", {"application_id": "APP-1001"}, lo, None, "FORBIDDEN_OPERATION"),
        ("HUMAN-01", "High-impact action blocked", "disburseLoan", {"account_id": "ACC-101"}, lo, None, "FORBIDDEN_OPERATION"),
        ("PARAM-01", "Missing member ID", "retrieve_member_record", {}, lo, None, "INVALID_PARAMETERS"),
        ("PARAM-02", "Missing application ID", "retrieve_member_record", {"member_id": "SACCO-M-001", "require_application_id": True}, lo, None, "INVALID_PARAMETERS"),
        ("PARAM-03", "Invalid parameter format", "retrieve_member_record", {"member_id": "INVALID"}, lo, None, "INVALID_PARAMETERS"),
        ("FAIL-01", "Data service unavailable", "retrieve_member_record", {"member_id": "SACCO-M-001"}, lo, "service_unavailable", "SERVICE_UNAVAILABLE"),
        ("FAIL-02", "Draft service unavailable", "create_case_draft", {"member_id": "SACCO-M-001"}, lo, "service_unavailable", "SERVICE_UNAVAILABLE"),
        ("FAIL-03", "Malformed tool response", "retrieve_member_record", {"member_id": "SACCO-M-001"}, lo, "malformed_response", "INVALID_TOOL_RESPONSE"),
        ("FAIL-04", "Incomplete response", "retrieve_member_record", {"member_id": "SACCO-M-001"}, lo, "incomplete_response", "INVALID_TOOL_RESPONSE"),
        ("FAIL-05", "Tool timeout", "retrieve_member_record", {"member_id": "SACCO-M-001"}, lo, "timeout", "TOOL_TIMEOUT"),
        ("DRAFT-01", "Authorized draft creation", "create_case_draft", {"member_id": "SACCO-M-001"}, lo, None, "SUCCESS"),
        ("CALC-01", "Repayment schedule math", "run_financial_calculation", {"calculation_type": "repayment_schedule", "inputs": {"principal": 5000000, "annual_interest_rate": 18, "term_months": 12}}, lo, None, "SUCCESS"),
        ("CALC-02", "Debt Service Ratio math", "run_financial_calculation", {"calculation_type": "debt_service_ratio", "inputs": {"net_monthly_income": 1500000, "existing_monthly_obligations": 200000, "proposed_monthly_installment": 300000}}, lo, None, "SUCCESS"),
    ]

    all_passed = True
    for test_id, desc, tool, params, usr, sim_fail, expected_status in test_runs:
        res = orch.execute_tool(tool, params, usr, simulate_failure=sim_fail)
        passed = (res["status"] == expected_status)
        if not passed:
            all_passed = False
        badge = " [PASS] " if passed else " [FAIL] "
        print(f"{badge} {test_id:8} | {desc:38} | Status: {res['status']:22} (Expected: {expected_status})")

    print("-" * 75)
    if all_passed:
        print("  ALL 16 ORCHESTRATION & TOOL TESTS PASSED SUCCESSFULLY!")
    else:
        print("  SOME TESTS FAILED.")
    print("=" * 75)
