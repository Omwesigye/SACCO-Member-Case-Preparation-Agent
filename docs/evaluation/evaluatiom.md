# Evaluation & Quality Assurance Index

This directory contains the complete evaluation datasets, prompt benchmarks, RAG grounding tables, and failure analyses for the **SACCO Member Case Preparation Agent**.

Per Week 2, 3, and 7 capstone specifications:
> *"Produce evidence that the system is sufficiently reliable, grounded, inspectable and safe for its bounded use case."*

---

## 1. Evaluation Artifacts Directory

| Artifact | File Link | Scope | Key Metrics / Findings |
|---|---|---|---|
| **Prompt Evaluation Table** | [prompt-evaluation-table.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/docs/evaluation/prompt-evaluation-table.md) | 10 baseline synthetic member profiles | Evaluates policy rule checking, prompt follow-through, and boundary enforcement. 9/10 passed cleanly; identified `EXCEPTION_REQUIRED` for loan arrears. |
| **RAG Grounding & Refusal Table** | [RAG-evaluation-table.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/docs/evaluation/RAG-evaluation-table.md) | 15 targeted policy questions | 5 answerable, 5 partially answerable, 5 unanswerable. Measures precision of citations and safe refusal behavior on out-of-corpus topics. |
| **50-Scenario Evaluation Dataset** | [30+ scenario evaluation dataset and results.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/docs/evaluation/30+%20scenario%20evaluation%20dataset%20and%20results.md) | 50 comprehensive scenarios | Covers Normal (6), Edge (12), Incorrect Member Info (7), Adversarial Prompts (9), Tool Failures (8), and Unauthorized Actions (8). |
| **Failure Catalogue & Remediation** | [failure-catalogue.md](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/docs/evaluation/failure-catalogue.md) | 8 failure and control cases | Documents 3 observed weaknesses (F-01 to F-03), 4 verified safeguards (F-04 to F-06, F-08), and 1 pending test (F-07). |

---

## 2. Automated Regression Test Suite

All safety guardrails, orchestration layers, deterministic calculators, and persistent memory features are covered by **44 automated pytest cases** in the [tests/](file:///c:/Users/USER/OneDrive/Desktop/SACCO%20PROJECT/SACCO-Member-Case-Preparation-Agent/tests/) directory:

- `test_guardrails.py` (12 tests)
- `test_persistent_memory.py` (7 tests)
- `test_rag_pipeline.py` (7 tests)
- `test_tools_orchestration.py` (18 tests)

**Result:** 44/44 passed (100% pass rate).
