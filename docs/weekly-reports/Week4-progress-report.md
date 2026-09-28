# Week 4 Progress Report

**Group name:** Group X
**Project name:** SACCO Member-Case Preparation Agent
**Week ending:** 25th September 2026

## Work Completed Against Weekly Objectives

- Defined two core agent tools with full input/output schemas, authorization rules, validation requirements, and failure behaviour: `retrieve_member_record` (retrieves synthetic member data) and a deterministic financial calculation tool (originally scoped as `run_financial_calculation`, later implemented more fully as a dedicated SACCO Credit Calculation Tools module).
- Implemented a working deterministic calculation engine in Python, exposed as a WSGI API (`POST /calculate`), supporting five distinct calculation types: reducing-balance repayment schedule, Debt Service Ratio (single and three-method variants), savings-based loan limit, security/collateral coverage, and guarantor coverage — all using fixed formulas with `Decimal` precision, never AI-generated arithmetic.
- Confirmed the calculation engine enforces the tool-catalogue contract exactly: it validates required fields, rejects invalid or missing inputs with specific error codes (e.g. `missing_or_invalid_field`, `invalid_input_value`, `unsupported_calculation_type`), and flags loan terms outside the 6–24 month policy range with a `policy_range_warning` rather than silently accepting them.
- Documented the **Human Approval Gate**: a formal control layer separating actions the agent may perform directly (retrieval, calculation, draft case creation) from actions that require explicit human authorization (loan approval/rejection, fund disbursement, account modification, final decision submission). Defined the full approval workflow, request/decision data structures, and six human-approval test cases (HA-01 to HA-06), including an explicit rule preventing the agent from ever approving its own request.
- Produced a full **Tool Authorization and Failure-Handling Test Plan** covering four test categories — missing parameters, authorization, service failure, and unexpected tool responses — with 14 defined test cases (AUTH-01 to AUTH-04, PARAM-01 to PARAM-03, FAIL-01 to FAIL-05, DRAFT-01, HUMAN-01), each with a stated scenario, input, and expected result.
- Established the core security principle governing all tool use: authorization and validation live in the application/orchestration layer, never in the foundation model — so no prompt, however phrased, can cause a tool to bypass authentication, role checks, or the human approval gate.

## Key Engineering Decisions and Why

- Split calculation logic into five distinct calculation types under one contract (`run_calculation`) rather than one rigid repayment-only function, since the policy corpus (identified during Week 3 RAG testing) references several distinct financial checks — DSR, savings multiplier, security coverage, guarantor coverage — not just repayment scheduling.
- Used Python's `Decimal` type with fixed rounding (`ROUND_HALF_UP`) throughout the calculation engine rather than floating-point arithmetic, to guarantee that UGX amounts are exact and reproducible — critical given this tool handles real financial math the AI is explicitly barred from generating itself.
- Designed the Human Approval Gate so that approval decisions are validated independently of the language model: a user typing "I approve this loan" in chat must have zero effect, since the application layer authenticates the approver's identity and role outside of any model-generated text. This directly closes the most obvious prompt-injection risk for a financial agent.
- Wrote authorization/failure test cases before full implementation, so the test plan defines the expected contract (what "rejected," "unauthorized," and "service unavailable" must look like) independently of whichever team member builds the enforcement code — keeping design and implementation properly decoupled.

## Failures/Challenges and Current Response

- The originally scoped `create_case_pack_draft` tool was reconsidered mid-week in favour of prioritizing the calculation tool, since deterministic financial arithmetic was judged the higher-risk, higher-priority capability to lock down first, given this project's core safety principle (established back in the Week 1 Charter) that AI must never perform financial calculations itself.

## Links to Repository and Task Board
- GitHub repository: https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
- ClickUp board: https://app.clickup.com/1200410000000434/v/l/t/1200410000000434
- Live application: https://sacco-member-case-preparation-agent-bzbryaduwvsuifpyzbu5fx.streamlit.app/

## Plan for Next Week

- Execute the 14 defined authorization/failure test cases against the live implementation and capture real evidence (request, response, pass/fail) for each.
- Wire the calculation engine and Human Approval Gate into the Streamlit application's case-preparation workflow.
- Update the architecture diagram to reflect the orchestration layer's authorization checks and the human-approval interception point.
- Begin drafting the case-pack creation/draft-record tool as a follow-on to the calculation tool.
