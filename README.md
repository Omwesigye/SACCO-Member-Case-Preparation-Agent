Project Charter
Problem Statement
SACCO staff currently spend significant time manually searching policy documents to answer member questions about loan procedures, savings rules, and repayment terms, and manually calculating illustrative repayment schedules before a member's case can reach a decision-maker. This slows response times, produces inconsistent explanations across staff, introduces calculation errors, and leaves no structured or traceable record of how a case was prepared. There is currently no tool that consolidates policy lookup, procedural explanation, and case preparation into a single guided, auditable workflow while keeping actual financial decisions under human control.

Target User
Primary user: SACCO  loan officers who respond to member inquiries and prepare member cases for internal review.
Secondary beneficiary: SACCO members themselves, who benefit indirectly through faster, clearer, and more consistent answers to procedural questions, and faster case turnaround.

Current Pain Point
Staff manually search paper or PDF-based policy documents to answer member questions about loan eligibility, procedures, interest structures, and savings rules.
Illustrative loan/savings schedules are calculated by hand or in ad hoc spreadsheets, increasing the risk of arithmetic error and inconsistency between staff.
Case notes prepared for staff/committee review are assembled manually with no standard structure, making review slower and harder to audit.
There is no searchable or traceable record showing which policy clause or document informed a given answer or case brief.
Staff time that could go toward higher-value member service and case review is instead spent on repetitive lookup and calculation tasks.

 AI-Native Value Proposition
Where AI adds value:
Retrieval and grounding (RAG): The system retrieves relevant clauses from a controlled set of SACCO policy documents so that procedural answers are grounded in actual source text rather than the model's general knowledge, reducing the risk of hallucinated policy.
Reasoning and explanation: The model explains procedures and requirements to staff/members in clear, plain language, adapting explanations to the specific case context.
Workflow planning (bounded agent): The system plans and executes a short, multi-step workflow  interpreting the query, retrieving relevant policy, gathering the relevant (synthetic) member record, invoking a calculation tool, and assembling a structured case brief for human review.

Where deterministic software/human judgement must remain in control:
All financial calculations (e.g interest and repayment schedule computation) are performed by explicit, testable code and never generated freeform by the model to eliminate arithmetic hallucination risk.
Access authorization and record validation (e.g confirming a member ID exists, confirming which staff member may view which case) is handled by deterministic application logic.
Final decisions e.g loan approval, disbursement, or any account change remain entirely with human staff/committees; the agent's output is always a prepared case for review, never an executed decision.
Scope
The project will focus on one primary end-to-end workflow in which a SACCO staff member submits a member case request, after which the agent retrieves relevant information from the controlled SACCO policy corpus, gathers the relevant synthetic member information, and invokes a deterministic calculation tool when an illustrative loan or savings schedule is required. Using the retrieved information and calculation results, the agent prepares a structured case brief containing the relevant policy information, procedural explanation, illustrative figures, and supporting details.The draft brief is then routed to an authorised staff member for human review and approval before simulated submission to the Credit Committee or review staff. The agent does not approve loans, change accounts, disburse funds, or make real financial transactions. 
The system will use a controlled corpus of approximately 10–50 public or team-authored SACCO policy documents with recorded provenance, together with a synthetic member-record dataset created by the team. The agent will have access to two to four explicitly defined tools, such as policy retrieval, an illustrative schedule calculator, and case-ticket creation. The agent workflow will be bounded by defined iteration limits, approved tools, and safe stop conditions. The project will also include one justified persistent-memory feature, such as retaining the active case and its relevant context across a session.

Success Criteria
At least 90% of answerable policy test questions return an answer supported by cited policy evidence. When the corpus does not support an answer, the system returns a clear insufficient-evidence response rather than inventing a policy rule. 
Illustrative schedule calculations match independently/manually verified figures exactly, since these are computed deterministically rather than generated by the model.
Every case the agent prepares is routed to a human staff member for review before any further action can occur, no case is auto-approved or auto-actioned.
The end-to-end workflow (from query to completed case brief) completes within a small, bounded number of agent steps, demonstrating controlled rather than open-ended autonomy.
The system can be demonstrated, inspected (via traces/logs), and explained by every member of our team.

Assumptions
Our team will source or approximate representative SACCO policy documents (e.g., publicly available cooperative handbooks/guidelines) or author a realistic synthetic policy set if authorized real documents are unavailable.
All member data used will be synthetic and created by our team ,no real, confidential, or personally identifiable SACCO member data will be used at any point.
We will have continued access to a foundation model API throughout the semester for development and evaluation.
SACCO procedures used are representative of general Ugandan SACCO practice rather than any one specific institution's confidential internal policy.

Constraints
The project must be completed within the 8-week semester timeline and remain small enough to be fully built, tested, and explained by every group member.
No confidential, proprietary, or personally identifiable data may be used at any stage of development or evaluation.
Any high-impact or financially-relevant action must be gated behind explicit human approval; the agent may never self-authorize such actions.
The system must remain inspectable, all agent decisions and tool calls must be traceable through logs.

 Project Summary
Our system helps SACCO staff prepare member cases by retrieving relevant policy information, generating clear procedural explanations, calculating illustrative schedules, and producing a structured case brief for human review. AI will handle retrieval, explanation, and workflow planning, while deterministic software will handle calculations, validation, and authorization. The agent will not approve loans, disburse funds, alter accounts, or perform real financial transactions. The system will use team-created/public SACCO policies and synthetic member data.
Primary end to end workflow
The SACCO Member Case Preparation Agent supports one primary workflow: a credit/loan officer prepares a complete, traceable member loan case for Credit Committee or review staff consideration. The agent assists with preparation only. It does not make a credit decision, change a member account, disburse funds, or conduct a real financial transaction. 

Steps
What happens
Output and control
1.Application intake 
The credit/loan officer enters a member application and attaches the permitted supporting documents. The system creates a case ID and checks that required fields and consent are present. 
A draft case and missing-items list. The case remains incomplete if required information is absent. 
2.Record and policy retrieval
The system retrieves the relevant synthetic member record and approved policy passages. It compares declared information with available records and identifies inconsistencies. 
A source register showing verified, declared, missing or contradictory information. Material differences require clarification. 
3.Eligibility checks
Configured rules assess membership status, product eligibility, KYC status, arrears, exposure limits, affordability threshold, and guarantor or security requirements. 
Pass, fail, pending-evidence or exception-required result for each rule, with rule ID and supporting source. 
4.Illustrative schedule
The deterministic calculator uses the requested amount, approved illustrative rate, term and repayment frequency to produce a reducing-balance repayment schedule. 
An illustrative schedule and affordability view. It is labelled illustrative and is not a loan offer or approval. 
5.Draft assessment
The agent prepares a case summary that separates verified facts from unresolved items. It presents policy results, schedule, risks, mitigants and any exception required. 
A draft assessment for the credit officer. The agent may request review but cannot approve, decline or recommend credit
6.Case pack assembly
The system assembles the application, evidence register, policy-check summary, schedule, risk/exceptions summary and audit trail into an indexed draft pack. 
A complete or not-ready draft case pack. Mandatory omissions prevent progression. 
7.Human review and submission
The credit officer reviews the pack. Following explicit approval, the system creates a simulated submission record for the Credit Committee or review staff. 
A submission status and audit event. The workflow ends; the human review group makes the final decision. 

Agent boundary
The agent may retrieve approved policy text, identify missing information, summarise verified evidence, invoke deterministic eligibility and schedule tools, and assemble a draft case pack. It must stop and hand off when information is incomplete, policy evidence is contradictory, an exception is required, a compliance flag appears, an approved tool fails, or a human decision is needed.
The Credit Committee or review staff retains authority to interpret exceptions, approve, decline or defer the case, and authorise any later operational action. This keeps the workflow useful for case preparation while ensuring that high-impact financial decisions remain human controlled.
Testable user stories with acceptance criteria 
Stakeholders include members or applicants, loan officers, Credit Committee or review staff, compliance or risk staff where escalation is required, SACCO management, system administrators and internal auditors. The loan officer is the primary user of the agent; other stakeholders provide information, review outputs, make decisions or receive audit evidence. 

US-LO1-Policy ingestion and search
As a loan officer, I want the system to ingest and index our credit policy, so that I can quickly check rules while preparing cases.
Acceptance criteria:
Given an uploaded credit policy (PDF/Word), when ingestion completes, then the system can return specific clauses on request.
Policy version and effective date are displayed on all references.
Ingestion errors (unreadable file, missing sections) are flagged for admin review

US-LO2-Eligibility check with reasons
As a loan officer, I want the system to check a synthetic member’s eligibility against policy and show reasons, so that I can advise members accurately.
Acceptance criteria:
Given member inputs (or synthetic profile) and a loan type, when eligibility is run, then the system returns Pass/Fail/Conditional with explicit reasons for example  “membership 4 months; policy requires 6”).
All reasons cite the relevant policy section.
Results are saved in the case file for audit.

US‑LO3 – Illustrative schedule computation
As a loan officer, I want the system to compute illustrative repayment schedules using our interest method, so that I can show members realistic options.
Acceptance criteria:
Given loan amount, tenor, interest method, fees, and grace period (if any), when the schedule is calculated, then it outputs a month‑by‑month table with principal, interest, total due, and due dates.
Calculations match a deterministic reference calculator within rounding tolerance.
Multiple scenarios (for example 12 vs 18 months) can be generated and compared side‑by‑side.

US-LO4-Case pack assembly and edit
As a loan officer, I want to assemble and edit a case pack before sending it to the committee, so that I can ensure accuracy and completeness.
Acceptance criteria:
Given eligibility and schedule results, when the case pack is generated, then it includes member summary, eligibility result, schedule, policy references, document checklist, and recommendation.
The loan officer can edit narrative fields and recommendations; edits are logged with user ID and timestamp.
The case pack status changes to “Staff‑Reviewed” after edits are saved.

US-LO5 -Synthetic profile upload for training
As a loan officer, I want to upload synthetic member profiles, so that I can train staff without using real member data.
Acceptance criteria:
Given a upload synthetic profile request, then profile details can be added
Profiles can be tagged by loan type and complexity for training scenarios.
The system prevents exporting synthetic profiles with any real member identifiers.

US-CC6-Standardized case pack view
As a Credit Committee member, I want to view standardized case packs, so that I can review applications consistently and efficiently.
Acceptance criteria:
Given a submitted case pack, when opened by a committee member, then it displays all required sections (summary, eligibility, schedule, policy refs, documents, recommendation).
Navigation between sections is clear (for example tabs or numbered sections).
Case packs for the same loan type have consistent structure.

US-CC7-Decision recording with conditions
As a Credit Committee member, I want to record my decision (approve/decline/modify) and any conditions, so that the outcome is clear and actionable.
Acceptance criteria:
Given a case pack, when the committee records a decision, then the system captures Approve/Decline/Modify, conditions  and approver identity.
The decision cannot be submitted without at least one authorized approver.
The decision is locked after submission; changes require a formal amendment workflow.

US-CC8-Policy citation visibility
As a Credit Committee member, I want to see which policy sections support the recommendation, so that I can verify compliance quickly.
Acceptance criteria:
Given a case pack, when viewed, then all policy citations are shown with section numbers and short excerpts.
Clicking a citation opens the relevant policy excerpt or reference.
Any deviation from policy is highlighted and requires justification.

US-MG9-Policy change impact visibility
As SACCO management, I want to understand how policy changes affect eligibility and schedules, so that I can make informed decisions.
Acceptance criteria:
Given a proposed policy change for example interest rate adjustment when a simulation is run on sample profiles, then the system shows impact on eligibility rates and average installments.
Results are presented in simple tables/charts.
Simulations are clearly labeled as  what if and not used for live decisions.

US-AU10-Full audit trail and policy version traceability
As an internal auditor, I want a complete immutable audit trail for each case pack showing the policy version used, so I can verify compliance and trace decisions .
Acceptance criteria:
Given a case ID, the audit view lists all key actions (creation, edits, eligibility checks, schedule generation, committee decision) with user IDs and timestamps. 
The view shows the exact policy version and date used for eligibility and schedule calculations. 
Archived policy versions are accessible to auditors 
Audit logs are immutable for regular users. 
Any mismatch between case logic and the referenced policy version is flagged 
Logs and policy details can be exported for audit working papers. 

US-SA11-Policy document management
As a system administrator, I want to upload and version credit policy documents, so that the system always uses the approved version.
Acceptance criteria:
Given a new policy document, when uploaded, then the admin can set it as “draft,” “approved,” or “archived.”
Only “approved” policies are used for live eligibility/schedule calculations.
Previous versions remain accessible for audit.

US-SA12-User and role management
As a system administrator, I want to manage users and roles (loan officer, committee, auditor, etc.), so that access is appropriate and secure.
Acceptance criteria:
Given a new staff member, when the admin creates an account, then they can assign roles and permissions based on job function.
Role changes take effect immediately and are logged. 
Inactive users can be deactivated without data loss.
The AI Boundary Matrix for the SACCO Member‑Case Preparation Agent 
The AI Boundary Matrix for the SACCO Member-Case Preparation Agent defines the limits between AI-assisted actions, deterministic system processing, and decisions that remain with authorised human staff. 
The AI may retrieve and summarise relevant passages from approved policy documents, explain procedures in plain language, identify missing or conflicting case information, and draft a structured case brief. Policy documents are uploaded, approved, versioned, and made available for retrieval through deterministic administrative controls. 
Deterministic components handle user authentication and role-based access, member-record validation, policy-rule evaluation, illustrative repayment calculations, case-status transitions, and audit logging. The illustrative schedule calculator uses fixed formulas and configured policy parameters so that calculations are reproducible and auditable. 
Human review is required for policy approval, unresolved evidence, compliance flags, policy exceptions, staff review of the case pack, and simulated Committee submission. The Credit Committee or review staff remains responsible for approving, declining, or deferring a case. The agent prepares the case; it does not score members, recommend credit, approve loans, change accounts, disburse funds, or perform financial transactions.
The project uses only public or team-authored policy documents and team-created synthetic member records.
No live SACCO data, confidential information, or real financial action is included. Audit logs automatically record policy references, calculation inputs and outputs, tool calls, user actions, and timestamps. Internal auditors may review these logs, but the agent does not certify compliance. 
