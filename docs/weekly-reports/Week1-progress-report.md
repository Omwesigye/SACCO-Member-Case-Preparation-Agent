BSE4104 — AI-Native & Agentic Engineering Capstone
Week 1 Progress Report

1. Group and Project
Group name: [Group X]    
Project name: SACCO Member-Case Preparation Agent 

2. Work Completed Against Weekly Objectives
●	Selected and scoped the SACCO member-case preparation use case, confirming it as feasible for an 8-week build: an agent that helps loan officers prepare a complete, policy-checked, auditable case pack for Credit Committee review, without making or executing any credit decision itself.
●	Wrote the Project Charter, covering the problem statement (manual, inconsistent, error-prone policy lookup, schedule calculation, and case-note assembly), the primary user (loan officers) and secondary beneficiary (members), the current pain points, and the AI-native value proposition where AI (retrieval, explanation, workflow planning) adds value versus where deterministic logic and human judgement must remain in control (calculations, authorization, final decisions).
●	Defined project scope, assumptions and constraints, including the use of a controlled 10-50 document policy corpus with provenance, a team-authored synthetic member dataset, 2-4 explicitly defined tools, bounded agent iteration limits, and one justified persistent-memory feature (active case/session context).
●	Defined the single primary end-to-end workflow across seven steps: application intake → record and policy retrieval → eligibility checks → illustrative schedule computation → draft assessment → case pack assembly → human review and submission, with the agent boundary explicit at each step (what the agent may do vs. where it must stop and hand off to a human).
●	Wrote 12 testable user stories with acceptance criteria across all stakeholder groups: loan officers (US-LO1 to LO5 policy ingestion, eligibility checks, schedule computation, case pack assembly, synthetic profile upload), Credit Committee (US-CC6 to CC8 standardized case view, decision recording, policy citation visibility), management (US-MG9 policy change impact simulation), auditors (US-AU10 full audit trail and policy version traceability), and system administrators (US-SA11, SA12 policy document and user/role management).
●	Built the AI Boundary Matrix, separating AI-permitted actions (policy retrieval/summarization, plain-language explanation, drafting case briefs, flagging missing/conflicting information) from deterministic-only actions (authentication/RBAC, record validation, rule evaluation, schedule calculation, status transitions, audit logging) and human-approval-required actions (policy approval, exception handling, case pack sign-off, simulated Committee submission).
●	Produced the initial system architecture: a three-tier layered design (presentation, application/business logic, data access) with RESTful APIs and role-based access control, covering role-specific dashboards, the loan workflow's separation of duties (member → loan officer → Credit Committee), and read-only auditor access for accountability.
●	Created the GitHub repository with the recommended folder structure and the ClickUp project, with Week 1 tasks assigned to owners.

3. Key Engineering Decisions and Why
●	Kept the agent strictly advisory across the entire workflow  it prepares and assembles the case pack but never scores, recommends, approves, or declines credit  so that all credit-risk authority stays with the human Credit Committee, directly matching the module's bounded-agency principle and reducing regulatory/compliance exposure.
●	Separated eligibility rule evaluation and repayment schedule arithmetic into deterministic, testable code rather than model-generated output, since these figures must be exact, reproducible, and auditable, and any arithmetic hallucination risk from the model is unacceptable in a financial context.
●	Chose a three-tier architecture with RBAC over a simpler monolithic design so that presentation, business logic, and data access responsibilities stay separable, supporting the different access needs of loan officers, the Credit Committee, management, administrators, and auditors, and improving testability and maintainability across the eight-week build.
●	Restricted the project to public/team-authored policy documents and fully synthetic member data, with an explicit constraint against any real or confidential SACCO data at any stage, to remove privacy/authorization risk from the outset rather than retrofitting it later.
●	Defined explicit agent stop/hand-off conditions (incomplete information, contradictory policy evidence, exceptions, compliance flags, tool failure) at the charter stage, ahead of building anything, so that bounded autonomy is a design constraint from Week 1 rather than an afterthought added during hardening.
4. Challenges and Current Response
●	Sourcing representative SACCO policy documents real institutional policy is confidential, so the team is assembling a synthetic/public-handbook-based corpus and documenting provenance for each source, per the charter's assumptions.
●	Scoping the eligibility rule set without a real policy to reference, responding by drafting a representative rule set based on general Ugandan SACCO practice and validating it is realistic enough to test against.

5. Repository and Task Board Evidence
GitHub repository:https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent.git
ClickUp board: https://app.clickup.com/1200410000000434/v/l/t/1200410000000434

6. Plan for Next Week (Week 2)
●	Select and document the foundation model to use (capability, cost, latency, privacy, access considerations) Model Selection Note 
●	Integrate the chosen model into the application for the first working baseline interaction (e.g., answering a policy question in plain language).
●	Write Prompt Specification v1.0 (role, task, context, constraints, output format, failure behavior) for the retrieval/explanation capability, and version at least two meaningful iterations.
●	Build a 10-case prompt evaluation table recording expected vs. actual behavior.
●	Begin assembling the controlled policy corpus and synthetic member dataset ahead of Week 3's RAG work.
●	Prepare the Week 2 progress report.
