# Week 2 Progress Report

**Group name:** Group X
**Project name:** SACCO Member-Case Preparation Agent
**Week ending:** 11th September 2026

## Work Completed Against Weekly Objectives
- Selected OpenAI GPT-5, accessed via the OpenAI API, as the foundation model, and integrated it into the application powering the AI Case Preparation step of the workflow. GPT-5 was chosen for its policy interpretation, retrieval-grounded explanation, missing-information detection, and structured case-summary capabilities, matching the case-preparation workflow's needs.
- Built and deployed a working baseline application (Streamlit) implementing the full intake-to-case-brief workflow: application intake → member/policy retrieval → deterministic eligibility checks → illustrative repayment calculation → AI-generated case brief → output validation → human review handoff.
- Ran the baseline model against 10 distinct synthetic member profiles, each designed to test a specific rule or edge case (clean pass, missing KYC, term violations above and below the allowed range, membership shortfall, arrears, combined simultaneous failures, high debt-to-income, zero guarantors, and a clean control case), producing 10 genuine, real case-brief outputs.
- Completed a full 10-case prompt evaluation table using real application outputs — no cases relied on invented or assumed data.
- Verified that deterministic repayment calculations and rule-check results are correct and consistent with the underlying member data in every case, and that the AI never approves, declines, or recommends a lending outcome.
- Identified and root-caused a genuine defect: the output validator uses simple keyword matching and cannot distinguish the AI stating it will NOT do something from actually doing it, causing repeated false-positive flags on the AI's own negation statements (e.g. Cases 1, 2, and 9).
- Found and reported a second defect during testing: a missing comma in the application's hardcoded member-selection list caused two filenames to be concatenated into one invalid string, crashing the app when that member was selected. Reported to the team for a one-line fix.
- Discovered that the system uses a third status category, EXCEPTION_REQUIRED, for arrears cases — more severe than a simple PASS/PENDING_EVIDENCE/FAIL — worth documenting formally as part of the system's status vocabulary.

## Key Engineering Decisions and Why
- Kept output validation as a separate post-processing layer from generation, which made it possible to isolate the false-positive issue as a validator-logic problem rather than a model-behaviour problem — the AI's actual behaviour was correct and boundary-respecting in every case.
- Selected GPT-5 over alternative models primarily for its reasoning, document-understanding, structured-output, and tool-integration capabilities, accepting the trade-offs of API cost, variable latency, and dependency on an external service (documented fully in the Model Selection Note); the team will monitor token usage and may substitute a smaller, lower-cost model for tasks that do not require GPT-5-level reasoning if evaluation shows it is adequate.

## Failures/Challenges and Current Response
- Output validator false-positive/keyword-matching defect: the validator flags any occurrence of "recommend approval"/"recommend rejection"/"recommend approving" regardless of negation, firing on 3 of the 10 real test cases. Response: scheduled for Week 3/7 rework to use context-aware or semantic checking instead of raw substring matching; in the meantime, the team will standardize the AI decision-boundary phrasing to avoid those literal trigger phrases.
- Guarantor status granularity: the system currently returns the same PENDING_EVIDENCE status whether a member has 0 guarantors or 2-3 unconfirmed guarantors, which are meaningfully different situations. Response: flagged as a design improvement for later refinement of the rule-checking logic.

## Links to Repository and Task Board
- GitHub repository: https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
- ClickUp board: https://app.clickup.com/1200410000000434/v/l/t/1200410000000434
- Live application: https://sacco-member-case-preparation-agent-bzbryaduwvsuifpyzbu5fx.streamlit.app/

## Plan for Next Week (Week 3)
- Assemble the controlled SACCO policy corpus and begin RAG pipeline implementation.
- Create at least 15 RAG test questions and document at least three retrieval/grounding failures.
