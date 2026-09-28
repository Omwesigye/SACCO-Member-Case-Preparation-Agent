Human Approval Gate
1. Purpose
The Human Approval Gate is a control mechanism that ensures the SACCO Member-Case Preparation Agent cannot independently perform higher-impact actions. The agent may retrieve information, analyze a case, perform calculations and prepare draft records but consequential actions must be reviewed and approved by an authorized human staff member.
The Human Approval Gate therefore provides a human-in-the-loop control between the AI agent and sensitive or higher-impact operations.
The principle is; The agent can prepare and recommend actions but an authorized human must approve consequential actions before execution.
2. Actions That Do Not Require Approval
Low-risk, read-only operations can be executed directly when the user is authorized.
Examples include:
•	retrieving an authorized member's application information;
•	retrieving SACCO policy information;
•	retrieving loan requirements;
•	calculating an illustrative repayment schedule;
•	creating a draft case-preparation record.
These operations should still pass authentication, authorization, parameter validation and tool-response validation.
3. Actions That Require Human Approval
Actions with a higher potential impact must be stopped at the Human Approval Gate until an authorized staff member explicitly approves them.
Examples include:
•	approving a loan;
•	rejecting a loan;
•	changing a member's financial information;
•	changing loan terms;
•	disbursing funds;
•	executing a financial transaction;
•	modifying an existing account;
•	submitting a final decision to another SACCO system.
These actions are outside the normal authority of the Member-Case Preparation Agent.
4. Approval Workflow
When the agent encounters an action requiring approval, the request follows this process:
![images alt](https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent/blob/f927abe0d7ea0ff5585f2072a2f6779b40481076/Screenshot%20from%202026-09-24%2013-37-19.png)
 
6. Approval Request
An approval request should contain enough information for the human reviewer to understand what is being requested.
Example:
{
  "requestId": "APR-2026-001",
  "action": "LOAN_APPROVAL",
  "applicationId": "APP-1001",
  "requestedBy": "Loan Officer",
  "reason": "Request to approve prepared loan case",
  "caseSummary": "Loan case has been prepared using the available member information and applicable SACCO policies.",
  "status": "PENDING_APPROVAL"
}
The system should not execute the requested action while the request has a PENDING_APPROVAL status.
7. Approval Decision
The authorized staff member can make one of the following decisions:
APPROVED
REJECTED
The decision should be associated with:
•	approval request ID;
•	reviewer identity;
•	decision;
•	date/time;
•	action requested;
•	reason or comment where required.
For example:
{
  "requestId": "APR-2026-001",
  "status": "APPROVED",
  "approvedBy": "Authorized Staff",
  "decisionTime": "2026-09-24T10:30:00",
  "comment": "Reviewed and approved for processing."
}
8. Rejected Approval
If the human reviewer rejects the request, the action must not be executed.
Example:
Agent
  ↓
Requests higher-impact action
  ↓
Human Approval Gate
  ↓
Authorized Staff
  ↓
REJECT
  ↓
Action blocked
  ↓
Agent receives rejection status
The agent may then inform the Loan Officer that the requested action was not approved.
The agent must not attempt to bypass the rejection by making the same request through another tool.
9. Authorization of the Approver
The Human Approval Gate must also verify that the person approving an action has the required authority.
For example:
User submits approval
        ↓
Authenticate user
        ↓
Check user role
        ↓
Check required permission
        ↓
Check approval request
        ↓
Approve / Reject
A normal agent user must not be able to approve an action simply by sending a message such as:
"I approve this loan."
The application must verify the user's authenticated identity and authorization independently of the language model.
10. Preventing Agent Self-Approval
A critical security rule is that the AI agent must never be able to approve its own action.
The following flow is prohibited:
Agent
  ↓
Requests approval
  ↓
Agent approves request
  ↓
Action executed
Instead:
Agent
  ↓
Requests approval
  ↓
Human Approval Gate
  ↓
Authorized Human
  ↓
Approval Decision
  ↓
Application validates approval
  ↓
Action may proceed
This ensures that the approval is an independent human decision.
11. Failure Handling
The Human Approval Gate must also handle failures safely.
Scenario	Expected Behaviour
No approver available	Keep request pending
Unauthorized approver	Reject approval attempt
Approval request expired	Do not execute action
Duplicate approval	Ignore duplicate or flag it
Rejected request	Do not execute action
Invalid approval request	Reject request
Approval service unavailable	Keep action pending
Missing reviewer identity	Reject approval
Agent attempts self-approval	Block request
Tool fails after approval	Report tool failure; do not claim success

A particularly important rule is: Approval does not guarantee successful execution.
For example, if a human approves an action but the downstream service is unavailable, the system must report that the action was approved but could not be executed. The agent must not report that the action was completed.
11. Audit Trail
Every approval request and decision should be recorded for accountability.
The audit record should contain:
Request ID
Action requested
Application/Case ID
Requesting user
Approving user
Approval status
Decision
Timestamp
Reason/comment
Execution status
Example:
Request ID:       APR-2026-001
Action:           LOAN_APPROVAL
Application:      APP-1001
Requested By:     Loan Officer
Approved By:      Authorized Staff
Decision:         APPROVED
Decision Time:    24 Sept 2026 10:30
Execution Status: PENDING
This provides traceability for internal review and auditing.
12. Human Approval Test Cases
HA-01: Approval Required
Scenario: Agent requests a higher-impact operation.
Expected: Request is intercepted by the Human Approval Gate and placed in PENDING_APPROVAL.
HA-02: Authorized Human Approves
Scenario: An authorized staff member reviews and approves the request.
Expected: Approval is recorded and the application may proceed with the authorized action.
HA-03: Unauthorized User Attempts Approval
Scenario: A user without the required permission attempts to approve the request.
Expected: Approval is rejected and the action remains pending.
HA-04: Human Rejects Action
Scenario: Authorized staff rejects the requested operation.
Expected: Action is not executed.
HA-05: Agent Attempts Self-Approval
Scenario: The agent attempts to approve its own request.
Expected: The application blocks the request.
HA-06: Approved Action Encounters Tool Failure
Scenario: Human approval is successfully recorded, but the downstream service becomes unavailable.
Expected: The system reports execution failure. The agent must not claim that the action was completed.
13. Design Principle
The Human Approval Gate establishes a clear separation between AI assistance and human authority.
The SACCO Member-Case Preparation Agent can:
•	retrieve information;
•	retrieve policies;
•	analyze available information;
•	perform illustrative calculations;
•	prepare case summaries;
•	create draft records.
However, the agent cannot independently:
•	approve or reject loans;
•	disburse money;
•	modify member accounts;
•	execute financial transactions;
•	make final lending decisions.
Therefore, the architecture follows the principle; AI prepares and assists; authorized SACCO staff review and decide.
This Human Approval Gate provides an additional safety boundary between the agent's reasoning capabilities and consequential SACCO operations.

