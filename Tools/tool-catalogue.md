# Tool Catalogue — SACCO Member-Case Preparation Agent

This document defines the tools/functions the AI agent is permitted to call. Each tool has a strict input/output schema, authorization rules, and defined failure behaviour, so the AI can only act within clearly bounded, auditable limits.

---

## Tool 1: retrieve_member_record

**Purpose**
Retrieves a synthetic SACCO member's profile data (membership duration, KYC status, savings, obligations, etc.) from the controlled synthetic dataset, so the AI can prepare a case without inventing member details.

**Input Schema**
```json
{
  "member_id": {
    "type": "string",
    "required": true,
    "pattern": "^SACCO-M-[0-9]{3}$",
    "description": "Unique synthetic member identifier, e.g. SACCO-M-001"
  }
}
```

**Output Schema**
```json
{
  "member_id": "string",
  "full_name": "string",
  "membership_months": "integer",
  "monthly_income": "number",
  "monthly_savings": "number",
  "savings_balance": "number",
  "existing_monthly_obligations": "number",
  "kyc_status": "enum [verified, missing, unverified]",
  "has_arrears": "boolean",
  "number_of_guarantors": "integer",
  "data_type": "string (always 'synthetic')",
  "record_found": "boolean"
}
```

**Authorization Rules**
- Callable only by the AI agent within an active case-preparation session — not exposed as a public/direct endpoint.
- Restricted to the synthetic dataset directory only; the tool has no code path to any real/production member database.
- No write access — this tool is strictly read-only.

**Validation Requirements**
- `member_id` must match the required pattern before lookup is attempted.
- Reject the call with a clear error if `member_id` is missing, empty, or malformed.

**Failure Behaviour**
- Missing/malformed ID → `{"record_found": false, "error": "invalid_member_id_format"}`
- ID well-formed but not found → `{"record_found": false, "error": "member_not_found"}`
- Data source unavailable → `{"record_found": false, "error": "data_source_unavailable"}` — agent must not fabricate placeholder member data.

---

## Tool 2: run_financial_calculation

**Purpose**
Performs all deterministic financial calculations needed during case preparation — repayment schedules, Debt Service Ratio (DSR), savings-based loan limits, and security/guarantor coverage — using fixed formulas only. The AI selects which calculation to run and supplies the required inputs, but never performs the arithmetic itself. This keeps every number in a case brief exact, reproducible, and auditable.

**Input Schema**
```json
{
  "calculation_type": {
    "type": "enum",
    "required": true,
    "options": ["repayment_schedule", "debt_service_ratio", "savings_loan_limit", "security_coverage"],
    "description": "Which calculation to perform"
  },
  "inputs": {
    "type": "object",
    "required": true,
    "description": "Fields required vary by calculation_type"
  }
}
```

**Inputs required per calculation_type:**

| calculation_type | Required inputs |
|---|---|
| repayment_schedule | principal, annual_interest_rate, term_months |
| debt_service_ratio | net_monthly_income, existing_monthly_obligations, proposed_monthly_installment |
| savings_loan_limit | savings_balance, multiplier_rate |
| security_coverage | loan_principal, total_pledged_security |

**Output Schema**
```json
{
  "calculation_type": "string (echoes the request)",
  "result": "object — fields depend on calculation_type, see below",
  "is_illustrative": "boolean (always true)",
  "calculation_successful": "boolean"
}
```

**Result fields per calculation_type:**

| calculation_type | Result fields |
|---|---|
| repayment_schedule | monthly_payment, total_interest, total_repayment |
| debt_service_ratio | dsr_percentage, within_policy_limit (true if ≤50%) |
| savings_loan_limit | max_eligible_loan_amount |
| security_coverage | coverage_percentage, meets_minimum_coverage (true if ≥100%) |

**Authorization Rules**
- Callable only by the AI agent within an active case-preparation workflow.
- Purely computational — no access to member records, no write access, no connection to any live financial system.
- The tool cannot output words like "approved," "offer," "qualifies," or "final" in any result — only numeric/boolean outputs. It states facts, never a verdict.

**Validation Requirements**
- `calculation_type` must be one of the four allowed values.
- All inputs required for that specific calculation_type must be present and numeric.
- Numeric inputs must be positive where applicable (e.g., principal > 0, term_months > 0).

**Failure Behaviour**
- Unknown calculation_type → `{"calculation_successful": false, "error": "unsupported_calculation_type"}`
- Missing/non-numeric required input → `{"calculation_successful": false, "error": "missing_or_invalid_field: <field_name>"}` — the AI must not estimate the figure itself.
- Invalid value (e.g., principal ≤ 0) → `{"calculation_successful": false, "error": "invalid_input_value: <field_name>"}`
- term_months outside the policy range (6–24 months) for repayment_schedule → still calculates and returns figures, but adds `"policy_range_warning": "term_exceeds_or_below_policy_limit"`
- Unexpected internal error → `{"calculation_successful": false, "error": "calculation_error"}` — agent must halt and report the fault, never substitute a guessed number.

