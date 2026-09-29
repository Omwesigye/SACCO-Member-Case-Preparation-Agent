# Grounded RAG Pipeline Test Documentation

## Overview
Automated tests for the Grounded RAG Pipeline are implemented in [test_rag_pipeline.py](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/tests/test_rag_pipeline.py).

## Test Cases

| Test Case | Objective | Expected Result | Status |
|---|---|---|---|
| `test_ingestion_loads_rag_documents` | Verify all 20 RAG policy files are parsed with frontmatter and section headers. | At least 20 chunks ingested; all chunks have `chunk_id`, `source_id`, `title`, `content`. | **PASS** |
| `test_retriever_finds_membership_eligibility` | Search for membership tenure and minimum shares requirements. | Returns `SACCO-CREDIT-001` Section 3 ("General Borrower Eligibility Criteria"). | **PASS** |
| `test_retriever_finds_debt_service_ratio` | Search for Debt Service Ratio (DSR) and affordability rules. | Returns `SACCO-CREDIT-001` Section 5 with 50% threshold. | **PASS** |
| `test_retriever_finds_kyc_requirements` | Search for Level 2 KYC requirements (NIN, LC1 letter). | Returns KYC / AML policy clauses. | **PASS** |
| `test_citation_formatting` | Verify citation string structure matches provenance standard. | Citation contains `Source ID`, `Doc`, `Section`. | **PASS** |
| `test_insufficient_evidence_handling` | Query unrelated topic (e.g. quantum computing / cryptocurrency). | Emits `INSUFFICIENT EVIDENCE` flag and refuses to speculate. | **PASS** |
| `test_case_evidence_retrieval` | Multi-dimensional retrieval for member profile with arrears and low tenure. | Retrieves top policy clauses and injects into case prompt. | **PASS** |

## Execution Command
```powershell
python -m pytest tests/test_rag_pipeline.py -v
```

All 7 test cases executed and passed.

---

# Tool Authorization, Orchestration, and Failure Handling Test Documentation

## Overview
Automated tests for tool authorization, human approval gate, schema validation, failure handling, and deterministic arithmetic are implemented in [test_tools_orchestration.py](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/tests/test_tools_orchestration.py) matching [Test_Authorisation_and_FailureHandling.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/Tools/Test_Authorisation_and_FailureHandling.md).

## Test Cases

| Test Case | Category | Objective / Scenario | Expected Result | Status |
|---|---|---|---|---|
| `test_auth_01_authorized_retrieval` | Authorization | Authorized Loan Officer retrieves member case information. | Status `SUCCESS`, data retrieved. | **PASS** |
| `test_auth_02_unauthorized_role` | Authorization | Unauthorized role attempts member data retrieval. | Status `UNAUTHORIZED`, operation blocked. | **PASS** |
| `test_auth_03_unauthenticated_request` | Authorization | Tool call received without valid authenticated user. | Status `AUTHENTICATION_REQUIRED`. | **PASS** |
| `test_auth_04_forbidden_high_impact_action` | Authorization | Agent attempts prohibited loan approval (`approveLoan`). | Status `FORBIDDEN_OPERATION`. | **PASS** |
| `test_human_01_human_approval_gate` | Human Gate | High-impact actions (`disburseLoan`, `modifyAccount`, `creditScoring`). | Status `FORBIDDEN_OPERATION` (Human Gate enforced). | **PASS** |
| `test_param_01_missing_member_id` | Parameters | Incomplete request without `member_id`. | Status `INVALID_PARAMETERS`. | **PASS** |
| `test_param_02_missing_application_id_when_required` | Parameters | Missing `application_id` when workflow requires it. | Status `INVALID_PARAMETERS`. | **PASS** |
| `test_param_03_invalid_parameter_format` | Parameters | Malformed identifier format rejected before lookup. | Status `INVALID_PARAMETERS`. | **PASS** |
| `test_fail_01_member_data_service_unavailable` | Resilience | Member data storage service unavailable. | Status `SERVICE_UNAVAILABLE` (no fabrication). | **PASS** |
| `test_fail_02_draft_service_unavailable` | Resilience | Case draft service unavailable. | Status `SERVICE_UNAVAILABLE`. | **PASS** |
| `test_fail_03_malformed_tool_response` | Validation | Non-conforming tool output detected by orchestrator. | Status `INVALID_TOOL_RESPONSE`. | **PASS** |
| `test_fail_04_incomplete_tool_response` | Validation | Partial response missing required schema fields. | Status `INVALID_TOOL_RESPONSE`. | **PASS** |
| `test_fail_05_tool_timeout` | Resilience | Service timeout handled gracefully without assumptions. | Status `TOOL_TIMEOUT`. | **PASS** |
| `test_draft_01_authorized_draft_creation` | Workflow | Authorized Loan Officer generates preliminary draft record. | Status `SUCCESS`, unique `draftId` returned. | **PASS** |
| `test_calc_01_repayment_schedule` | Calculator | Reducing-balance schedule deterministic math. | Status `SUCCESS`, exact UGX payment schedule. | **PASS** |
| `test_calc_02_debt_service_ratio` | Calculator | Debt Service Ratio computation and policy limit check. | Status `SUCCESS`, exact DSR percentage. | **PASS** |
| `test_calc_03_savings_loan_limit` | Calculator | Savings multiplier loan ceiling calculation. | Status `SUCCESS`, exact loan ceiling. | **PASS** |
| `test_calc_04_security_coverage` | Calculator | Collateral/security coverage ratio computation. | Status `SUCCESS`, coverage percentage. | **PASS** |

## Execution Commands
```powershell
# Run the automated test suite
python -m pytest tests/test_tools_orchestration.py -v

# Run the live demonstration runner with formatted output
python tests/test_tools_orchestration.py
```

All 18 test cases executed and passed.

