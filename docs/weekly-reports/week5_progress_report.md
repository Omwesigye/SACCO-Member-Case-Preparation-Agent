WEEK 5 PROGRESS REPORT
Agent Architecture and Bounded Autonomy
1. Introduction
During Week 5, the SACCO Member-Case Preparation Agent was extended from a tool-enabled assistant into a bounded, goal-directed agent workflow. The main objective was to enable the agent to perform a multi-step task by selecting appropriate actions from a predefined set of approved tools while maintaining clear limits on what it can do.
The selected workflow focuses on preparing a member loan case for review by a Loan Officer. This task benefits from multi-step decision making because the agent may need to retrieve member information, retrieve relevant SACCO policies, identify missing information, perform illustrative calculations, and prepare a structured case before determining that the task is complete.
The workflow was designed around the following agent cycle:
Sense/Context → Plan/Decide → Act/Tool → Observe → Stop/Re-plan
Boundaries were also established through maximum iterations, approved tools, stop conditions, and human hand-off requirements.
2. Goal-Directed Task
The task selected for the bounded agent workflow was:
Prepare a structured loan case for review by an authorized SACCO Loan Officer using available member information, SACCO policies, and approved calculation tools.
The agent does not make the final lending decision. Its responsibility is to gather and organize relevant information and prepare the case for human review.
The workflow may require the agent to:
    1. understand the loan officer's request;
    2. retrieve the relevant member/application information;
    3. retrieve applicable SACCO policies;
    4. determine whether required information is available;
    5. perform an illustrative repayment calculation where appropriate;
    6. create a draft case-preparation record;
    7. stop when the preparation goal is complete;
    8. hand the case to a human when the agent cannot safely continue.
3. Agent Task Contract
A task contract was defined to establish the boundaries of the agent.
Component	Definition
Goal	Prepare a structured loan case for staff review
Approved Tools	Member Case Data Retrieval, Policy Retrieval, Schedule Calculator, Case Draft Creation
State	User request, member/application information, retrieved policies, calculations, tool results, current workflow step
Maximum Iterations	10
Maximum Tool Retries	1
Human Approval	Required for higher-impact actions
Stop Condition	Case successfully prepared
Failure Stop	Required tool unavailable after permitted retry
Information Stop	Critical information missing
Authorization Stop	Requested action is outside agent permissions
Safety Stop	Invalid or untrusted tool result
Scope	Case preparation only
The task contract ensures that the agent operates within a clearly defined scope rather than being allowed to decide its own capabilities.
4. Approved Tools
The agent is restricted to a defined set of tools.
4.1 Member Case Data Retrieval Tool
Used to retrieve authorized information about a member and their loan application.
Purpose:
Provide the agent with current application data required for case preparation.
4.2 Policy Retrieval Tool
Used to retrieve relevant SACCO policies, procedures, and requirements.
Purpose:
Ensure that the agent's case preparation is based on the controlled SACCO knowledge base developed during Week 3.
4.3 Schedule Calculator Tool
Used to perform illustrative loan repayment calculations.
Purpose:
Perform deterministic calculations rather than requiring the language model to calculate financial schedules itself.
4.4 Case Draft Creation Tool
Used to create a low-risk draft case-preparation record.
Purpose:
Store the prepared case for later review by authorized SACCO staff.
The tool does not approve the loan or execute any financial transaction.
5. Agent Decision Workflow
The agent follows five main stages.
5.1 Sense/Context
The agent receives the Loan Officer's request and identifies the information currently available.
For example:
Member ID: MEM-1024
Application ID: APP-1001
Requested Amount: UGX 5,000,000
Loan Period: 24 months
Purpose: Business expansion
The agent determines what information is already available and what information may need to be retrieved.
5.2 Plan/Decide
The agent selects the next action from the approved tools.
For example:
Required member information unavailable
        ↓
Select Member Case Data Retrieval Tool
After retrieving the information, the agent evaluates whether another action is necessary.
The agent therefore does not execute every tool automatically. It selects the next appropriate action based on the current state.
5.3 Act/Tool
The selected tool is executed through the application/orchestration layer.
The application layer validates:
    • user authorization;
    • tool authorization;
    • required parameters;
    • input format;
    • tool availability.
Only approved operations are allowed to execute.
5.4 Observe
After a tool executes, the agent observes the result.
Possible outcomes include:
    • successful data retrieval;
    • missing information;
    • invalid tool response;
    • service unavailable;
    • successful calculation;
    • successful draft creation.
The result becomes part of the current workflow state.
5.5 Stop/Re-plan
Based on the result, the agent either:
    • selects another approved action;
    • retries an allowed failed operation;
    • requests missing information;
    • stops the workflow;
    • hands the case to a human.
This prevents the agent from continuing indefinitely.
6. Stop Conditions and Human Hand-Off
The agent stops when:
    • the case has been successfully prepared;
    • critical information is missing;
    • an approved tool fails after the allowed retry;
    • a tool returns an invalid response;
    • the maximum number of iterations is reached;
    • an unauthorized action is requested;
    • the requested operation requires human approval.
For example, if the agent is asked to approve a loan, it must not attempt to execute the action.
Instead:
Loan Approval Requested
        ↓
Outside Agent Scope
        ↓
Human Approval / Decision Required
        ↓
Agent Stops
This maintains the human-in-the-loop principle established in Week 4.
7. Working Bounded Agent Workflow
The implemented workflow follows the following sequence:
Loan Officer Request
        ↓
Sense Context
        ↓
Identify Required Information
        ↓
Plan Next Action
        ↓
Call Approved Tool
        ↓
Observe Result
        ↓
Is More Information Required?
        │
     ┌──┴──┐
    Yes    No
     │      │
     ▼      ▼
 Re-plan   Prepare Case
     │      │
     └──┐   │
        ▼   ▼
     Continue
        │
        ▼
   Stop / Human Review
The workflow is bounded because the agent cannot select arbitrary tools or continue beyond the predefined iteration and retry limits.
8. Execution Trace 1; Successful Workflow
Trace ID: TRACE-001
The Loan Officer submits a complete loan application.
Execution
    1. Agent receives the loan application.
    2. Agent identifies that member information is required.
    3. Member Case Data Retrieval Tool is called.
    4. Member information is successfully returned.
    5. Agent determines that applicable loan policy is required.
    6. Policy Retrieval Tool is called.
    7. Relevant policy information is returned.
    8. Agent determines that an illustrative schedule can be generated.
    9. Schedule Calculator Tool is called.
    10. Calculation succeeds.
    11. Case Draft Creation Tool creates the draft.
    12. Agent stops because the preparation goal has been completed.
    13. Case is presented to the Loan Officer for review.
Result: Successful completion.
9. Execution Trace 2 — Missing Information
Trace ID: TRACE-002
The Loan Officer submits a loan application without specifying the loan period.
Execution
    1. Agent receives the application.
    2. Member information is retrieved successfully.
    3. Agent identifies that the loan period is missing.
    4. Agent determines that a repayment schedule cannot safely be calculated.
    5. Schedule Calculator Tool is not called.
    6. Agent requests the missing loan period.
    7. Workflow stops pending additional information.
Result: Safe stop.
The agent does not invent a loan period or assume a value from another application.
10. Execution Trace 3; Failure and Recovery
Trace ID: TRACE-003
The agent attempts to retrieve member information, but the Member Case Data Retrieval Tool is temporarily unavailable.
Execution
    1. Agent receives the application.
    2. Agent selects the Member Case Data Retrieval Tool.
    3. Tool returns SERVICE_UNAVAILABLE.
    4. Agent identifies that a retry is permitted.
    5. Agent performs one retry.
    6. The service remains unavailable.
    7. Maximum retry limit is reached.
    8. Agent stops the workflow.
    9. Case is handed back to the Loan Officer for manual verification.
Result: Failure handled safely.
The agent does not create or assume member information when the source system cannot provide it.
11. Execution Trace Evaluation
The captured traces were evaluated against the requirements for bounded autonomy.
Requirement	Evaluation
Goal-directed task	Achieved
Multi-step workflow	Achieved
Approved tools only	Achieved
Maximum iterations defined	Achieved
Retry limit defined	Achieved
Stop conditions defined	Achieved
Human hand-off defined	Achieved
Successful execution trace	Captured
Missing-information trace	Captured
Failure/recovery trace	Captured
Safe stopping	Demonstrated
The traces demonstrate that the agent can select appropriate next actions while remaining within predefined operational boundaries.
12. Challenges and Observations
One of the main challenges identified during the implementation was ensuring that the agent does not continue processing when required information or services are unavailable. This was addressed through explicit stop conditions and controlled recovery behaviour.
Another important observation was that tool results must be treated as part of the agent's state. The agent cannot simply call a tool and assume that it succeeded. It must observe and validate the result before deciding what to do next.
The use of execution traces also made it possible to identify whether the agent followed the intended workflow and whether failures resulted in safe stopping rather than unsupported assumptions.
13. Conclusion
During Week 5, the SACCO Member-Case Preparation Agent was developed into a bounded, goal-directed multi-step workflow. The selected task of preparing a member loan case benefits from agentic decision making because the system must determine which approved action to perform next based on the current case state.
The workflow implements the Sense/Context → Plan/Decide → Act/Tool → Observe → Stop/Re-plan cycle. A task contract was defined with approved tools, state information, iteration limits, retry limits, stop conditions, and human hand-off requirements.
Three execution traces were captured: a successful case-preparation workflow, a missing-information scenario, and a tool failure with recovery. These traces demonstrate that the agent can perform multiple steps while remaining within its defined boundaries.
The Week 5 implementation therefore demonstrates bounded autonomy rather than unrestricted autonomy. The agent can choose among approved next actions and perform useful multi-step case preparation, but it stops safely when it lacks sufficient information, encounters persistent tool failures, reaches its limits, or encounters an action requiring human authority.
