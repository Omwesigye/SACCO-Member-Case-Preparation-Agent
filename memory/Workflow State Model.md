
The SACCO Loan-Case Preparation Agent is designed to assist loan officers in preparing and understanding member loan cases. The loan officer feeds synthetic or approved case data into the system, and the agent uses that information, together with SACCO policy evidence and deterministic calculation tools, to prepare a draft case brief for staff review. 
The workflow state model defines the different stages through which a loan case moves, the information required at each stage, the events that move the case forward, and the conditions that require the agent to stop or hand over to a loan officer. The model makes the agent’s behaviour explicit, controlled, and auditable. It also ensures that the agent cannot silently approve a loan, change member records or make a final credit decision.

1. Case Received
The workflow begins when the loan officer submits a case-preparation request to the agent. At this stage, the officer provides the case identifier and the synthetic member and loan-case data required for preparation. The case identifier links the request to a specific member loan application, while the member and case data provide the information needed for policy checks and calculations.

The agent records the request, the initiating loan officer, the timestamp, and the selected loan product. It then validates that the officer is authorized to prepare the case and that the case identifier exists. If authorization fails, the workflow moves directly to a failed-safe state. If authorization succeeds, the workflow moves to the context-collection state.

The information collected at this stage includes the case ID, member ID, loan product, requested loan amount, requested repayment period, repayment frequency, first repayment date, loan purpose, proposed security, proposed guarantors, and the current case status. The agent does not create new member data at this stage; it only reads the information supplied by the loan officer or retrieved from the authorized synthetic case record.

2. Context Collection
In the context-collection state, the agent gathers the information needed to prepare the case. It retrieves the member record, the loan-case record, and the relevant SACCO policy evidence from the controlled RAG knowledge base.

The member record provides information such as membership duration, eligible savings, share capital, gross monthly income, net monthly income, existing loan balance, existing monthly debt, repayment status, and submitted documents. The loan-case record provides the requested loan amount, loan product, requested tenor, repayment frequency, first repayment date, loan purpose, proposed security, and proposed guarantors.

The agent then searches the approved SACCO policy corpus for the rules that apply to the selected loan product. It retrieves evidence such as minimum membership requirements, savings or share requirements, maximum loan amount, maximum tenor, interest method, required documents, security rules, guarantor rules, and approval limits. Each retrieved policy section is stored with its document title, version, section, page, approval status, and effective date.

The agent must use only approved and current policy documents for a new case. If the relevant policy evidence cannot be found, the policy is unclear, or the policy version is missing, the workflow moves to the handoff-required state. If the member record or case record is incomplete, the agent also moves to handoff so that the loan officer can provide or correct the information.

3. Validation
The validation state checks whether the case contains enough information to continue. The agent verifies that the required member fields, loan-case fields, and policy evidence are available. It also checks whether the selected loan product is recognized and whether the requested loan amount and repayment period are within the limits defined by the SACCO’s approved policy.

During validation, the agent checks whether the member has met the minimum membership period, whether the requested loan amount is within the savings-based limit, whether the requested tenor is allowed, and whether the required documents have been submitted. It also checks whether the member has an existing loan balance or existing monthly debt that may affect affordability.

If all required information is available, the workflow moves to the calculation state. If a required field is missing, a document is absent, the loan product is not recognized, or the requested amount exceeds the savings-based limit, the workflow moves to the handoff-required state. The agent does not guess missing values or assume that a member qualifies without evidence.

4. Calculation
The calculation state is where the agent calls deterministic financial tools. The language model does not perform arithmetic. It only determines which calculation is required and supplies the validated inputs. The calculation tool applies fixed formulas and returns exact, repeatable results.

The agent may call the repayment-schedule calculator to calculate the monthly installment, interest, principal repayment, opening balance, closing balance, fees, and due dates. It may call the DSR tool to assess affordability using gross income, net income, or disposable income. It may call the savings-based limit tool to determine the maximum loan amount supported by eligible savings. It may also call the security-coverage or guarantor-coverage tool to determine whether the proposed security or guarantors adequately cover the requested loan amount.

Each calculation result is stored in the case state together with the calculation version, input values, output values, policy version, and timestamp. This ensures that the calculation can be reproduced later by an auditor or another loan officer. If a calculation tool fails, the agent retries once. If it fails again, the workflow moves to the failed-safe state.

5. Assessment
In the assessment state, the agent compares the calculation results with the SACCO’s approved policy limits. It determines whether the requested loan amount is within the savings-based ceiling, whether the DSR is within the permitted threshold, whether the repayment period is acceptable, and whether the security or guarantor coverage meets the minimum requirement.

The agent identifies the case as complete, conditional, or requiring handover. A complete case has all required information, passes policy checks, and is ready for a draft case brief. A conditional case may be ready for review but has missing documents or a policy issue that must be resolved by the loan officer. A handover case has failed a policy limit, contains conflicting information, or requires an exception.

The agent does not decide whether the loan should be approved. It only reports the result of each check and identifies the reason for any failure. For example, it may state that the requested amount exceeds the savings-based ceiling, that the DSR is above the policy threshold, or that guarantor coverage is insufficient.

6. Drafting
In the drafting state, the agent prepares a structured draft case brief. The brief contains the member summary, loan request summary, policy references, eligibility findings, repayment schedule summary, DSR result, savings-based limit result, security or guarantor coverage result, required-document checklist, missing information, risk flags, and a recommended next step.

The agent clearly labels the output as a draft for staff review. It includes the policy version, calculation version, source citations, and audit trace ID. The draft case brief is saved using the draft-case-pack tool. The tool creates a draft record only; it does not submit the case to the Credit Committee, approve the loan, or issue a final repayment schedule to the member.

The agent’s recommendation is advisory. For example, it may recommend that the loan officer request missing documents, reduce the requested amount, obtain an additional guarantor, or refer the case to the Credit Committee. The loan officer remains responsible for reviewing the recommendation and deciding the next action.

7. Awaiting Loan Officer Review
The workflow stops in the awaiting-review state once the draft case brief has been created. At this point, the agent has completed its assigned task. The loan officer reviews the draft, verifies the policy evidence, checks the calculations, and decides whether the case should be corrected, submitted for Credit Committee review, or returned for further work.

The agent does not continue after this state. It cannot submit the case to the Credit Committee, approve the loan, decline the loan, or issue a final repayment schedule. Any submission, approval, rejection, or final communication must be performed by an authorized loan officer or Credit Committee member.

8. Handoff Required
The handoff-required state occurs when the agent cannot safely continue without human action. The agent stops and explains the reason for the handover. The loan officer is then responsible for resolving the issue and restarting or continuing the workflow where appropriate.

Common handoff reasons include missing member information, missing loan-case fields, missing required documents, unavailable policy evidence, unclear policy wording, conflicting policy versions, an unrecognized loan product, a requested amount above the savings-based limit, a DSR above the policy threshold, insufficient security coverage, insufficient guarantor coverage, or a request for a policy exception.

The agent must state the exact reason for the handover. For example, it may say that the requested amount exceeds the calculated savings-based ceiling, that the net-income DSR exceeds the configured limit, or that the required guarantor coverage has not been met. The agent must not attempt to solve the issue by inventing information or changing policy limits.

9. Failed Safe
The failed-safe state occurs when the workflow encounters a technical, authorization, or safety failure. The agent stops immediately to prevent incorrect or unauthorized actions. Examples include an unauthorized user, an invalid case ID, an unavailable member-record service, an unavailable policy service, a calculation-service failure, an unexpected tool response, or an attempt to call an unapproved tool.

When this happens, the agent preserves the audit trace, records the error code, and informs the loan officer that the workflow cannot continue safely. The agent does not create a draft case pack unless the information already collected is complete and valid. It also does not retry indefinitely. Each failed tool may be retried once, and if the retry fails, the workflow stops safely.

10. Completed
The completed state means that the agent’s assigned work has ended. This occurs after the loan officer has reviewed the draft case brief and taken the appropriate action. The agent may record that the case was reviewed, but it does not record a loan approval or rejection on its own.

The completed state does not mean that the loan has been approved. It only means that the agent’s case-preparation task has finished and that the case has moved into the human-controlled review process. The loan officer, Credit Committee, and other authorized SACCO staff remain responsible for all lending decisions.

