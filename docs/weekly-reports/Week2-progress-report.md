# Week 2 Progress Report

**Group name:** Group X
**Project name:** SACCO Member-Case Preparation Agent
**Week ending:** 11th September 2026

## Work Completed Against Weekly Objectives
- Selected Gemini as the foundation model and integrated it into the application powering the AI Case Preparation step of the workflow.
- Built and deployed a working baseline application (Streamlit) implementing the full intake-to-case-brief workflow: application intake → member/policy retrieval → deterministic eligibility checks → illustrative repayment calculation → AI-generated case brief → output validation → human review handoff.
- Ran the baseline model against all 3 available synthetic member profiles, each twice, producing 6 genuine outputs to test both correctness and run-to-run consistency.
- Completed a full 10-case prompt evaluation table using real application outputs — no cases relied on invented or assumed data.
- Verified across all runs that rule-checking results (PASS/PENDING/FAIL) and deterministic repayment calculations are perfectly consistent between repeated runs of the same input, while natural-language phrasing varies slightly, as expected of a generative model.
- Identified and root-caused a genuine defect: the output validator uses simple keyword matching and cannot distinguish the AI stating it will NOT do something from actually doing it, causing inconsistent false-positive flags depending on which exact phrasing the model happened to generate.

## Key Engineering Decisions and Why
- Ran each test member twice rather than only once — this turned out to be essential, since a single run per member would have hidden the validator's non-deterministic false-positive behaviour; two of the three members flagged differently on their second run than their first.
- Kept output validation as a separate post-processing layer from generation, which made it possible to isolate this as a validator-logic problem rather than a model-behaviour problem — the AI's actual behaviour was correct and boundary-respecting in all 6 runs.

## Failures/Challenges and Current Response
- Output validator false-positive/keyword-matching defect: the validator flags any occurrence of "recommend approval"/"recommend rejection" regardless of negation. Response: scheduled for Week 3/7 rework to use context-aware or semantic checking instead of raw substring matching; in the meantime the team will standardize the AI's decision-boundary phrasing to avoid those literal trigger phrases.
- Synthetic dataset limited to 3 member profiles restricts variety of scenarios (no arrears=true case yet). Response: dataset expansion planned for Week 3 alongside policy corpus assembly.

## Links to Repository and Task Board
- GitHub repository: https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
- ClickUp board: https://app.clickup.com/1200410000000434/v/l/t/1200410000000434
- Live application: https://sacco-member-case-preparation-agent-bzbryaduwvsuifpyzbu5fx.streamlit.app/

## Individual Contribution Summary
- [member — task owned — evidence, per teammate]

## Plan for Next Week (Week 3)
- Fix the validator's keyword-matching false-positive issue with context-aware checking.
- Expand the synthetic member dataset to include more edge cases (arrears=true, unverified guarantors, 0-month membership).
- Assemble the controlled SACCO policy corpus and begin RAG pipeline implementation.
- Create at least 15 RAG test questions and document at least three retrieval/grounding failures.
