The SACCO Loan-Case Preparation Agent is a bounded, goal-directed decision-support system for Ugandan SACCO loan case preparation. Its purpose is to help a loan officer prepare a complete, policy-grounded, and auditable draft case brief, but it must never approve a loan, disburse money, change member balances, change member records and perfome calculations
The agent uses controlled SACCO policy documents, synthetic member records, deterministic calculation tools and human review. This is appropriate because SACCO credit policy must define loan repayment conditions, maximum borrowing, and acceptable loan security; the agent should apply and explain those rules, while lending authority remains with humans

Goal and scope
    The agent’s goal is to prepare a draft loan case brief for a SACCO loan officer by retrieving the member record and loan application, finding relevant policy evidence, performing approved deterministic calculations, identifying missing requirements or risks, and creating a draft case pack for human review
    The agent supports a single primary workflow: generation of loan case preparation. It can later be adapted for other products 

Expected outcome
AWAITING_LOAN_OFFICER_REVIEW: The draft case brief is complete and ready for a loan officer to review   
HANDOFF_REQUIRED: The agent cannot proceed because information is missing, policy evidence is unclear, a policy limit failed, or an exception is required.
FAILED_SAFE: The agent encountered an authorization, tool, system, or safety failure and stopped without taking an unsafe action
The agent should never output “Loan Approved.” Instead, it should use language such as “Draft case brief prepared. It is pending loan officer review”

Contents of the draft case brief
A complete draft case brief should include:
Case ID and member ID.
Loan product.
Requested loan amount.
Requested repayment period.
First proposed repayment date.
Membership duration.
Eligible savings and share capital.
Existing loan balance and existing monthly debt.
Gross income, net income, and disposable-income information where required.
Policy version, document title, clause, section, and page used.
Eligibility findings.
Repayment schedule summary.
DSR results.
Savings-based borrowing limit.
Security coverage or guarantor coverage.
Required-document checklist.
Missing information and risk flags.
Proposed next step.
Audit trace ID.
Statement that the output is an illustrative staff-review draft, not a loan approval.

Inputs and knowledge
The agent needs information from two distinct sources: the member record and the loan case record. It also needs approved SACCO policy information from the RAG knowledge base.

Member-record inputs: The Member Record Tool retrieves the member’s financial and membership profile. The agent should request only the minimum fields required for the current case
member_id: Identifies the SACCO member
Membership duration: Checks membership-period eligibility
Eligible savings balance: Supports savings-based loan limit calculation
Share capital: Supports eligibility where policy requires shares
Gross monthly income: Supports gross-income DSR
Net monthly income: Supports net-income DSR
Existing monthly debt: Used in DSR calculation
Existing loan balance: Used in savings-limit and exposure checks
Repayment status: Identifies arrears, delinquency, or current repayment status
Submitted documents: Confirms whether documents are available
Guarantor or security references: Supports coverage checks where applicable

Loan-case inputs:The Case Record Tool retrieves information from the specific loan application.
case_id	: Identifies the loan application
Loan product:Determines applicable product policy
Requested amount: Used for eligibility and all financial calculations
Requested tenor: Used for repayment-schedule calculation
Repayment frequency: Defines monthly, weekly, or other schedule type
First repayment date: Used to generate due dates
Purpose of loan: Supports product and risk assessment
Proposed security: Used for security-coverage calculation
Proposed guarantors:Used for guarantor-coverage calculation
Case status: Shows whether the case is draft, under review, or already decided
Previous notes: Provides context but must not override policy evidence

Policy and configuration inputs
The RAG policy source should provide only current, approved SACCO documents, including the credit policy, loan-product guidelines, savings policy, governance policy, and approved fee schedule. The policy configuration should contain:
Loan-product eligibility requirements.
Minimum membership period.
Savings and shares requirements.
Maximum borrowing amount.
Maximum repayment tenor.
Interest method and annual or monthly interest rate.
Processing fees and other approved charges.
DSR threshold.
Savings multiplier.
Required minimum security coverage.
Allowed collateral types and valuation haircuts.
Guarantor rules and approved-guarantee capacity rules.
Required supporting documents.
Approval limits and escalation rules.
Policy version and effective date.
The agent must use the current approved policy for new applications. Archived policy documents should be used only when an internal auditor reviews a historical case.

Workflow state and logic
The agent should follow a controlled state machine. It should not jump directly to a recommendation before retrieving the member record, loan case, policy evidence, and calculation results
RECEIVED: The system receives a case-preparation request
AUTHORIZATION_CHECK:The system verifies user role, case access, and permitted tools
CONTEXT_COLLECTION: The agent retrieves the member record, loan-case record, and policy evidence
VALIDATION: The agent checks required fields, documents, policy version, and loan-product rules	
CALCULATION: The agent calls deterministic financial tools	
ASSESSMENT: The system compares results against policy limits	
DRAFTING: The agent prepares a structured draft case brief and evidence summary	
AWAITING_LOAN_OFFICER_REVIEW: The workflow stops and waits for staff review	
HANDOFF_REQUIRED: The workflow stops because a human must resolve an issue	
FAILED_SAFE:A technical, permission, or safety failure occurs	
COMPLETED	The agent’s assigned work is finished	End

Sense, plan, act, observe, and stop cycle
The workflow should implement the following agent cycle:
Sense/Context — Retrieve the member record, loan case, and policy clauses.
Plan/Decide — Determine which calculations and checks are needed.
Act/Tool — Call only approved tools.
Observe — Review the tool result, policy evidence, and output status.
Re-plan — Perform another approved action only if a gap remains and limits have not been exceeded.
Stop — Create a draft case brief, hand over to staff, or stop safely after failure.
A normal workflow could be:
Receive case→Get member record→Get loan case→Retrieve policy→Validate data→Calculate schedule→Calculate DSR→Calculate limitscoverage→Prepare draft→Loan officer reviewReceive case→Get member record→Get loan case→Retrieve policy→Validatedata→Calculatschedule→CalculateDSR→Calculate limitscoverage→Prepare draft→Loan officer review

Approved tools and limits
The agent must use an explicit allow-list of tools. It should default to read-only access and call only the tool needed for the current workflow stage. Least-privilege tool access, field-level access restrictions, and runtime authorization checks are important because an agent should not be allowed to access or modify more data than required for its assigned task

Maximum workflow limits
aximum workflow iterations	6	Prevents agent loops and repeated planning
Maximum total tool calls	10	Keeps execution bounded and auditable
Maximum member-record retrievals	2	One normal attempt and one retry only
Maximum case-record retrievals	2	One normal attempt and one retry only
Maximum policy searches	3	Product rules, supporting requirements, and exception/document rules
Maximum calculation tool calls	5	Schedule, DSR, savings limit, security coverage, guarantor coverage
Maximum draft-case-pack creation calls	1	Prevents duplicate draft records
Maximum retry per failed tool	1	Stops repeated technical failures
Maximum re-planning attempts	2	Ensures safe handoff if the problem cannot be resolved

Stop conditions, prohibited actions, handover and approval
Stop conditions
The agent must stop when the case is complete, when human judgment is required, or when the system cannot continue safely.
Successful stop:
The agent stops with AWAITING_LOAN_OFFICER_REVIEW when:
The member record and case record were retrieved successfully.
The required policy evidence was retrieved.
Required information is complete.
The repayment schedule was calculated.
DSR was calculated where income applies.
Savings limit and security or guarantor coverage were checked where applicable.
Required documents were checked.
The draft case brief includes citations and calculation results.
The draft case pack was created.
No policy exception is pending.
The final agent statement should be:
“The draft case brief has been prepared using the current approved policy and deterministic calculations. It is awaiting loan officer review and is not a loan approval

Human-handover stop
The agent must stop with HANDOFF_REQUIRED if:
The member record is missing, incomplete, or inconsistent.
The loan application details are incomplete.
The member does not meet a basic eligibility rule.
The required policy section cannot be found.
Different policy documents appear to conflict.
A policy document is outdated, unapproved, or has no effective date.
The requested amount exceeds the savings-based loan limit.
The repayment tenor exceeds policy limits.
DSR exceeds the configured policy threshold.
Security coverage is below the required percentage.
Guarantor capacity is insufficient.
Required documents are missing.
An exception, restructuring, top-up, waiver, or rescheduling is requested.
Tool or iteration limits are reached.

Failed-safe stop
The system must stop with FAILED_SAFE when:
The user does not have permission to view the member or case.
A tool returns unauthorized or malformed data.
The member-record service fails twice.
The case service fails twice.
The policy retrieval service is unavailable.
A calculation service fails twice.
The agent tries to call an unapproved tool.
The agent reaches the maximum number of iterations or tool calls.
The system detects a conflict that cannot be resolved from approved evidence

Prohibited actions
The agent must never:
Approve, decline, or modify a loan decision.
Disburse funds.
Alter savings, share capital, loan balances, interest rates, penalties, repayment dates, or transaction history.
Change policy rules, policy versions, DSR thresholds, savings multipliers, or security haircuts.
Add a member, remove a member, or change member personal information.
Issue a binding repayment schedule to the member.
Submit a final loan approval message.
Send approval or rejection communication by SMS, email, or WhatsApp.
Delete draft case packs, audit logs, policies, or member records.
Retrieve data outside the assigned case or authorized role.
Use unapproved external internet information as if it were SACCO policy.
Invent missing values or assume missing policy rules.
Bypass loan-officer or Credit Committee approval.

Every tool call and approval should be logged with the case ID, user role, agent action, tool name, input, output, policy version, timestamp, result, and any human approval record. Agent audit trails should capture the identity, authorization decision, tool request, resource, approval state, and final outcome, not merely a list of tool calls.
This contract ensures that the SACCO agent can retrieve, calculate, explain, flag, and draft, while loan officers and the Credit Committee retain responsibility for all lending decisions.