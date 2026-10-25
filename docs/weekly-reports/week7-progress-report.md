Week 7 Report: Observability and Tracing Evidence
During Week 7, the project focused on implementing observability and tracing for the SACCO Member-Case Preparation Agent. The main deliverable was an observability_tracing.py module that records structured evidence for every agent workflow run, making the system inspectable, auditable, and safe.

The module generates two JSONL evidence files: agent_traces.jsonl, which stores a complete summary of each workflow, and agent_events.jsonl, which records individual actions such as state transitions, policy retrievals, tool calls, and safety events. Each run is assigned a unique trace ID and linked to a case ID, loan officer, role, and loan product.

The implementation records the agent’s workflow states, including RECEIVED, CONTEXT_COLLECTION, AWAITING_LOAN_OFFICER_REVIEW, HANDOFF_REQUIRED, and FAILED_SAFE. It also captures retrieved SACCO policy evidence, including document title, version, section, page, and effective date, demonstrating that responses are grounded in approved policy.

Tool-call evidence records the tool name, inputs, outputs, status, authorization, and errors. The system uses an approved tool allow-list and blocks unauthorized actions such as approve_loan. Workflow limits of six iterations and ten tool calls prevent uncontrolled execution.

Three demonstration traces were produced: a successful case-preparation workflow, a blocked unauthorized tool request, and a safe handover after missing policy evidence. Overall, Week 7 delivered practical evidence that the agent follows controlled workflows, uses approved tools and policy sources, stops safely when required, and supports audit and evaluation.