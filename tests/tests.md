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
