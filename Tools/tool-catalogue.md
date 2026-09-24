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

## Tool 2: create_case_pack_draft

**Purpose**
Performs a low-risk simulated side effect: assembles retrieved member data, policy evidence, and the deterministic repayment calculation into a draft case pack record, logged as "pending human review." Does not approve, reject, or disburse anything.

**Input Schema**
```json
{
  "member_id": { "type": "string", "required": true },
  "policy_evidence": { "type": "array", "required": true },
  "repayment_schedule": { "type": "object", "required": true },
  "policy_check_results": { "type": "array", "required": true }
}
```

**Output Schema**
```json
{
  "case_pack_id": "string",
  "status": "enum [DRAFT_READY_FOR_HUMAN_REVIEW, DRAFT_INCOMPLETE]",
  "created_at": "timestamp",
  "requires_human_review": "boolean (always true)",
  "confirmation_message": "string"
}
```

**Authorization Rules**
- May only be called after both `retrieve_member_record` and the deterministic calculator have successfully returned data for the same `member_id`.
- The output status can never be set to "approved," "rejected," or "disbursed" — those values do not exist in this tool's schema, so it is structurally incapable of making a lending decision.
- This is a simulated side effect only: writes to a local draft log/file, not any real SACCO system of record.

**Validation Requirements**
- All four input fields must be present and non-empty; if `policy_check_results` is missing any rule's outcome, the draft is marked `DRAFT_INCOMPLETE`.
- `repayment_schedule` must match the deterministic calculator's output format — figures that don't match the expected schema are rejected.

**Failure Behaviour**
- Missing required input → `{"status": "DRAFT_INCOMPLETE", "error": "missing_required_field: <field_name>"}`
- Repayment schedule fails schema validation → `{"error": "invalid_calculator_output"}`
- Unauthorized/out-of-sequence call → `{"error": "sequence_violation: member record and repayment schedule required first"}`

---
