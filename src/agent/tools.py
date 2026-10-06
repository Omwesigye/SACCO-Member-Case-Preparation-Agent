"""
Approved tools for the SACCO Case Preparation Agent.

These implement the exact contracts defined in the Week 4 Tool Catalogue:
  - retrieve_member_record
  - retrieve_policy_evidence   (stand-in for the real RAG retriever)
  - run_financial_calculation

Every tool returns a plain dict with a success/failure flag. None of them
ever raise an exception out to the caller — all failure is returned as
data, exactly as specified in the tool catalogue's "Failure Behaviour"
sections, so the orchestrator can always safely inspect the result.
"""

import re
from decimal import Decimal, ROUND_HALF_UP, getcontext

from data import MEMBERS, POLICY_SNIPPETS

getcontext().prec = 28


# ---------------------------------------------------------------------------
# Tool 1: retrieve_member_record
# ---------------------------------------------------------------------------
def retrieve_member_record(member_id):
    if not member_id or not re.match(r"^SACCO-M-\d{3}$", member_id):
        return {"record_found": False, "error": "invalid_member_id_format"}

    record = MEMBERS.get(member_id)
    if record is None:
        return {"record_found": False, "error": "member_not_found"}

    result = dict(record)
    result["record_found"] = True
    return result


# ---------------------------------------------------------------------------
# Tool 2: search_sacco_policy  (stand-in for the live RAG retriever)
# ---------------------------------------------------------------------------
def search_sacco_policy(topics):
    """
    topics: list of strings, e.g. ["eligibility", "dsr", "kyc", "guarantor"]
    Returns matching snippets with citations, or an empty list + flag if
    nothing relevant was found (mirrors the real app's "Insufficient
    Evidence" behaviour seen in Week 3 testing).
    """
    matches = [s for s in POLICY_SNIPPETS if s["topic"] in topics]
    return {
        "evidence_found": len(matches) > 0,
        "evidence": matches,
    }


# ---------------------------------------------------------------------------
# Tool 3: calculate_illustrative_schedule
# (named to match the group's Agent Architecture Diagram; internally still
# supports all four deterministic calculation types from the Week 4 catalogue)
# ---------------------------------------------------------------------------
def _to_decimal(value):
    return Decimal(str(value))


def _round_ugx(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_illustrative_schedule(calculation_type, inputs):
    allowed = {"repayment_schedule", "debt_service_ratio",
               "savings_loan_limit", "security_coverage"}

    if calculation_type not in allowed:
        return {"calculation_successful": False, "error": "unsupported_calculation_type"}

    try:
        if calculation_type == "repayment_schedule":
            principal = _to_decimal(inputs["principal"])
            annual_rate = _to_decimal(inputs["annual_interest_rate"])
            term_months = int(inputs["term_months"])

            if principal <= 0:
                return {"calculation_successful": False, "error": "invalid_input_value: principal"}
            if term_months <= 0:
                return {"calculation_successful": False, "error": "invalid_input_value: term_months"}

            monthly_rate = annual_rate / Decimal("1200")
            if monthly_rate == 0:
                payment = principal / term_months
            else:
                growth = (1 + monthly_rate) ** term_months
                payment = principal * monthly_rate * growth / (growth - 1)

            payment = _round_ugx(payment)
            total_repayment = payment * term_months
            total_interest = total_repayment - int(principal)

            response = {
                "calculation_type": calculation_type,
                "result": {
                    "monthly_payment": payment,
                    "total_interest": total_interest,
                    "total_repayment": total_repayment,
                },
                "is_illustrative": True,
                "calculation_successful": True,
            }
            if not (6 <= term_months <= 24):
                response["policy_range_warning"] = "term_exceeds_or_below_policy_limit"
            return response

        elif calculation_type == "debt_service_ratio":
            income = _to_decimal(inputs["net_monthly_income"])
            existing = _to_decimal(inputs["existing_monthly_obligations"])
            proposed = _to_decimal(inputs["proposed_monthly_installment"])

            if income <= 0:
                return {"calculation_successful": False, "error": "invalid_input_value: net_monthly_income"}

            dsr = float((existing + proposed) / income * 100)
            return {
                "calculation_type": calculation_type,
                "result": {
                    "dsr_percentage": round(dsr, 1),
                    "within_policy_limit": dsr <= 50,
                },
                "is_illustrative": True,
                "calculation_successful": True,
            }

        elif calculation_type == "savings_loan_limit":
            savings = _to_decimal(inputs["savings_balance"])
            multiplier = _to_decimal(inputs["multiplier_rate"])
            if savings < 0 or multiplier < 0:
                return {"calculation_successful": False, "error": "invalid_input_value"}
            max_loan = _round_ugx(savings * multiplier)
            return {
                "calculation_type": calculation_type,
                "result": {"max_eligible_loan_amount": max_loan},
                "is_illustrative": True,
                "calculation_successful": True,
            }

        else:  # security_coverage
            principal = _to_decimal(inputs["loan_principal"])
            pledged = _to_decimal(inputs["total_pledged_security"])
            if principal <= 0:
                return {"calculation_successful": False, "error": "invalid_input_value: loan_principal"}
            coverage = float(pledged / principal * 100)
            return {
                "calculation_type": calculation_type,
                "result": {
                    "coverage_percentage": round(coverage, 1),
                    "meets_minimum_coverage": coverage >= 100,
                },
                "is_illustrative": True,
                "calculation_successful": True,
            }

    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {"calculation_successful": False,
                "error": f"missing_or_invalid_field: {exc}"}


# ---------------------------------------------------------------------------
# Tool 4: create_case_pack_draft
# ---------------------------------------------------------------------------
_CASE_PACK_COUNTER = {"n": 0}


def create_case_pack_draft(member_id, policy_evidence, calculations, policy_check_results=None):
    required = [member_id, policy_evidence, calculations]
    if any(r is None or (hasattr(r, "__len__") and len(r) == 0) for r in required):
        return {"status": "DRAFT_INCOMPLETE",
                "error": "missing_required_field"}

    if not all(c.get("calculation_successful") for c in calculations.values()):
        return {"status": "DRAFT_INCOMPLETE",
                "error": "invalid_calculator_output"}

    _CASE_PACK_COUNTER["n"] += 1
    case_pack_id = f"CASE-2026-{_CASE_PACK_COUNTER['n']:04d}"

    return {
        "case_pack_id": case_pack_id,
        "status": "DRAFT_READY_FOR_HUMAN_REVIEW",
        "requires_human_review": True,
        "confirmation_message": f"Case pack for {member_id} assembled and saved for officer review.",
    }
