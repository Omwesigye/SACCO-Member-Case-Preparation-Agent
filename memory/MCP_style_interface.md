SACCO Member-Case Preparation Agent
1. Introduction
As part of Week 6, the SACCO Member-Case Preparation Agent was extended to support interoperability through a clearly defined MCP-style interface.
The purpose of the interface is to expose approved SACCO capabilities to the agent through well-defined tools with explicit inputs, outputs, permissions, and security boundaries.
Rather than allowing the AI model to access databases or application services directly, the agent communicates with application capabilities through controlled interfaces. This creates a separation between the agent's reasoning and the underlying SACCO systems.
The interface follows the principle:
The agent requests a capability through a defined interface; the application validates authorization and executes the capability.
The interface is designed around the existing capabilities of the Member-Case Preparation Agent.
2. MCP-Style Interface Concept
The interface exposes capabilities as tools rather than exposing internal implementation details.
For example, the agent does not need to know:
    • how the SACCO database is structured;
    • which SQL queries are used;
    • which Java classes access the database;
    • where policy documents are physically stored;
    • how the repayment calculation is implemented.
Instead, it interacts with clearly defined capabilities such as:
get_member_case()
retrieve_policy()
calculate_schedule()
create_case_draft()
This improves interoperability because the underlying implementation can change without requiring the agent's decision-making logic to change.
3. Interface 1 —Retrieval Member Record
Capability
get_member_case
Purpose
Retrieve authorized information about a member's loan application for case preparation.
Inputs
{
  "memberId": "MEM-1024",
  "applicationId": "APP-1001"
}
Input Requirements
Input	Type	Required	Description
memberId	String	Yes	Unique member identifier
applicationId	String	Yes	Loan application identifier
Output
{
  "status": "SUCCESS",
  "memberId": "MEM-1024",
  "applicationId": "APP-1001",
  "loanAmount": 5000000,
  "loanPeriod": 24,
  "loanPurpose": "Business expansion",
  "existingLoan": false
}
Possible Responses
SUCCESS
NOT_FOUND
UNAUTHORIZED
INVALID_PARAMETERS
SERVICE_UNAVAILABLE
Permission
Only authenticated and authorized SACCO users with permission to access the relevant loan case may invoke this capability.
Security Boundary
The tool must not expose unrelated member information. The application must enforce access control before returning the data.
4. Interface 2 — Policy Retrieval
Capability
retrieve_policy
Purpose
Retrieve relevant SACCO policies, procedures, or guidelines needed for case preparation.
Inputs
{
  "query": "documents required for a business loan"
}
Output
{
  "status": "SUCCESS",
  "results": [
    {
      "document": "Business Loan Policy",
      "section": "4.2",
      "content": "Required supporting documents...",
      "version": "2026.1"
    }
  ]
}
Permission
The capability can be accessed by the Member-Case Preparation Agent because it operates on the approved SACCO knowledge corpus.
Security Boundary
Only documents approved for use by the agent may be retrieved.
The interface must not allow the agent to arbitrarily access private or unrelated SACCO documents.
5. Interface 3 — run financial Calculation
Capability
calculate_schedule
Purpose
Perform deterministic illustrative loan repayment calculations.
Inputs
{
  "principal": 5000000,
  "annualInterestRate": 18,
  "periodMonths": 24
}
Output
{
  "status": "SUCCESS",
  "principal": 5000000,
  "periodMonths": 24,
  "monthlyPayment": 249624,
  "calculationType": "ILLUSTRATIVE"
}
Permission
The agent may use this tool for case preparation.
Security Boundary
The calculator only performs calculations. It does not:
    • approve a loan;
    • reject a loan;
    • disburse funds;
    • modify member accounts;
    • create financial transactions.
The result must therefore remain explicitly labelled as an illustrative calculation.
6. Interface 4 — Case Draft Creation
Capability
create_case_draft
Purpose
Create a low-risk draft containing the information prepared by the agent.
Inputs
{
  "applicationId": "APP-1001",
  "summary": "Business loan case prepared for staff review",
  "policyReferences": [
    "Business Loan Policy, Section 4.2"
  ],
  "missingInformation": [],
  "calculationIncluded": true
}
Output
{
  "status": "CREATED",
  "draftId": "DRAFT-2026-001",
  "reviewStatus": "PENDING_HUMAN_REVIEW"
}
Permission
Authorized Loan Officers may request draft creation through the agent.
Security Boundary
The capability creates only a draft.
It cannot:
    • approve the loan;
    • reject the loan;
    • disburse money;
    • modify the member account;
    • execute a financial transaction.
Any higher-impact action must pass through the Human Approval Gate established in Week 4.
7. Common Interface Response Structure
To improve interoperability, the tools use a consistent response structure.
Successful response
{
  "status": "SUCCESS",
  "data": {}
}
Failed response
{
  "status": "ERROR",
  "errorCode": "SERVICE_UNAVAILABLE",
  "message": "The requested service is currently unavailable."
}
This allows the agent orchestration layer to distinguish between successful results and failures.
8. Authentication and Authorization
The MCP-style interface must not rely on the language model to enforce security.
The request flow is:
Agent
  ↓
Tool Request
  ↓
Authentication
  ↓
Authorization
  ↓
Input Validation
  ↓
Tool Execution
  ↓
Output Validation
  ↓
Result Returned to Agent
The application/orchestration layer verifies:
    1. whether the user is authenticated;
    2. whether the user has permission to use the capability;
    3. whether the requested resource is within the user's scope;
    4. whether the input parameters are valid;
    5. whether the returned result conforms to the expected schema.
This prevents an agent-generated request from bypassing SACCO access-control mechanisms.
9. Security Boundaries
The interface establishes several security boundaries.
Boundary 1 — Agent and Database
The agent cannot directly access the SACCO database.
Agent → Interface → Authorized Service → Database
This prevents unrestricted database access by the model.
Boundary 2 — Agent and Sensitive Operations
The agent cannot directly execute high-impact financial operations.
Agent → Human Approval Gate → Authorized Human → Action
Boundary 3 — Agent and Policy Knowledge
The agent can only retrieve documents from the approved knowledge corpus.
Boundary 4 — User and Member Data
The application verifies whether the authenticated user has permission to access the requested member's information.
10. Failure Handling
The interface also defines standard failure behaviour.
Failure	Interface Response	Agent Behaviour
Missing input	INVALID_PARAMETERS	Request missing information
Unauthorized request	UNAUTHORIZED	Stop operation
Resource not found	NOT_FOUND	Inform user
Service unavailable	SERVICE_UNAVAILABLE	Retry if permitted
Timeout	TIMEOUT	Stop/retry according to limits
Invalid response	INVALID_RESPONSE	Reject result
Forbidden operation	FORBIDDEN	Human hand-off
The agent must never treat an error response as successful data.
11. Example End-to-End Interaction
A Loan Officer asks:
"Prepare the case for member MEM-1024's business loan application APP-1001."
The agent determines that several capabilities are required.
Step 1 — Retrieve member case
get_member_case(
    memberId="MEM-1024",
    applicationId="APP-1001"
)
The interface validates the request and returns authorized application information.
Step 2 — Retrieve policy
retrieve_policy(
    query="business loan requirements and supporting documents"
)
The policy interface returns relevant policy sections.
Step 3 — Calculate illustrative schedule
calculate_schedule(
    principal=5000000,
    annualInterestRate=18,
    periodMonths=24
)
The calculator returns the illustrative schedule.
Step 4 — Prepare draft
create_case_draft(
    applicationId="APP-1001",
    summary="Prepared loan case for staff review"
)
The system creates a draft.
Step 5 — Human review
Draft Created
      ↓
PENDING_HUMAN_REVIEW
      ↓
Loan Officer Reviews
The workflow stops at human review rather than allowing the agent to make a final lending decision.
12. Interoperability Benefits
The MCP-style interface provides several benefits.
Standardized capabilities
Each capability has a clearly defined name, input schema, output schema, and permission model.
Separation of concerns
The agent is responsible for deciding which approved capability is useful, while the application is responsible for authorization and execution.
Replaceable implementations
The underlying Java service, database, or calculation implementation can be changed without changing the conceptual tool interface.
Controlled access
The agent only receives capabilities that have explicitly been exposed to it.
Better monitoring
Each tool invocation can be logged with:
    • requesting user;
    • tool name;
    • input;
    • authorization result;
    • execution status;
    • output status;
    • timestamp.
This provides traceability for agent operations.
13. Security and Governance Principle
The MCP-style interface follows the principle of least privilege.
The agent receives only the capabilities necessary for its case-preparation task. It does not receive unrestricted access to SACCO systems.
The interface therefore separates:
What the agent can request
from
What the application is authorized to execute.
This distinction is important because a language model may generate a valid-looking tool request even when the requested operation should not be permitted.
14. Conclusion
The Week 6 MCP-style interface provides a clear interoperability boundary for the SACCO Member-Case Preparation Agent. Four controlled capabilities were defined: member case retrieval, policy retrieval, schedule calculation, and case draft creation.
Each capability has a defined purpose, input schema, output schema, permission model, and security boundary. Authentication, authorization, input validation, and output validation are performed by the application/orchestration layer rather than being delegated to the language model.
The interface allows the agent to interact with SACCO capabilities in a controlled and interoperable manner while maintaining the safety boundaries established in previous weeks. In particular, the agent remains restricted to case preparation and cannot independently perform loan approval, rejection, disbursement, account modification, or financial transactions.
The resulting design demonstrates how an agent can be connected to external capabilities through explicit, secure, and well-defined interfaces without giving the model unrestricted access to the underlying SACCO system.
