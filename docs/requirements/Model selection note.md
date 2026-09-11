
# Model Selection Note: OpenAI GPT-5

## Selected Model

The selected AI model for the SACCO Member Case Preparation Agent is **OpenAI GPT-5**, accessed through the OpenAI API. ChatGPT is the user-facing product, while the API allows the SACCO application to send controlled prompts and receive model responses programmatically.

GPT-5 is suitable because the project requires policy interpretation, retrieval-grounded explanations, missing-information detection, structured case summaries, and controlled interaction with application tools. The model will assist with preparing case packs but will not make, recommend, approve, or reject credit decisions.

## Capabilities and Suitability

GPT-5 can process natural-language instructions and retrieved policy content, summarize member information, explain applicable requirements, identify missing or conflicting information, and produce structured responses. These capabilities support the loan officer’s workflow:

**Application intake → Authorized record retrieval → Policy retrieval → Eligibility evaluation → Illustrative schedule calculation → Draft case assessment → Case-pack assembly → Human review**

The application may expose controlled functions such as:

- `retrieve_member_record()`
- `search_sacco_policy()`
- `calculate_illustrative_schedule()`
- `create_case_pack_draft()`

The model may request an appropriate tool, but the application will enforce authentication, authorization, validation, and tool permissions. Eligibility rules, financial calculations, status changes, audit logging, and final credit decisions will remain outside the model and will be implemented using deterministic code or human approval.

The model will be used with Retrieval-Augmented Generation (RAG). Relevant sections from the approved SACCO policy corpus will be retrieved and supplied to the model as evidence. Responses must cite the relevant policy source and should state when sufficient evidence is unavailable.

## Cost

OpenAI API usage is charged separately from a ChatGPT subscription. The project will use the official OpenAI API pricing page to record the current GPT-5 input and output token prices:

**Official pricing:** https://platform.openai.com/pricing

The estimated cost can be calculated as follows:

**Estimated cost = (input tokens ÷ 1,000,000 × input price) + (output tokens ÷ 1,000,000 × output price)**

Actual cost will depend on prompt length, retrieved policy content, response length, tool calls, and the number of test cases. To control cost, the project will:

- Send only the policy sections and member information required for each case.
- Avoid repeating unnecessary conversation history.
- Limit the maximum response length.
- Cache stable policy content where appropriate.
- Monitor token usage and API expenditure.
- Use a smaller, lower-cost model for tasks that do not require GPT-5-level reasoning, if evaluation shows that it is adequate.

The final report will record the prices applicable on the date of testing rather than relying on outdated estimates.

## Latency

GPT-5 latency is not fixed. It can vary depending on prompt size, reasoning effort, output length, number of tool calls, network conditions, and service load. A case involving several retrieval and tool calls will normally take longer than a simple question.

The project will measure:

- Time to first response token.
- Total response time.
- Total time for a complete case-pack workflow.
- Latency with and without tool calls.
- Success rate within the target response time.

For the prototype, the target is to return ordinary policy explanations within approximately **5–10 seconds** and complete a full case-pack preparation workflow within an acceptable time for loan-officer use. These are engineering targets, not guaranteed OpenAI service levels. Tests will use identical synthetic cases and record average and maximum latency.

## Privacy and Data Handling

The development system will use only synthetic member records and public or team-authored SACCO policy documents. Real member, financial, identity, or confidential SACCO information will not be sent to the API.

According to OpenAI’s API data-use documentation, API inputs and outputs are not used to train OpenAI models by default unless the customer explicitly opts in. OpenAI may retain limited data for abuse monitoring and security purposes, subject to the applicable retention controls and service terms. Organisations with approved requirements may be eligible for additional data-retention controls.

Before any production use, the project team must review the current OpenAI API data-processing, retention, security, and regional availability requirements. The application will also:

- Send only the minimum information required for each task.
- Remove unnecessary personally identifiable information.
- Apply authentication and role-based access control.
- Protect API keys using environment variables or a secret manager.
- Never expose API keys in frontend code or GitHub.
- Validate model responses before displaying or storing them.
- Maintain an audit trail of requests, retrieved policies, tool calls, and human actions.
- Require human review before a case pack is submitted to the Credit Committee.

## Access Requirements

The project requires:

- An OpenAI account with API access.
- An API key with appropriate project permissions.
- Internet access from the backend application.
- A backend such as Python/FastAPI or another HTTP-compatible service.
- Secure storage for the API key.
- The OpenAI SDK or HTTPS API client.
- A defined model name and API version confirmed from the current OpenAI documentation.

A ChatGPT web subscription alone does not automatically provide API credits or API access. API billing and ChatGPT subscriptions are separate.

## Final Assessment

GPT-5 is a strong candidate because its reasoning, document understanding, structured-output, and tool-integration capabilities match the SACCO case-preparation workflow. Its main disadvantages are API cost, variable latency, dependency on an external service, and the need for careful privacy controls.

The model will remain advisory. It will retrieve, explain, summarize, and draft, while deterministic application code and authorised staff will control calculations, access, exceptions, approvals, and final credit decisions.

**OpenAI documentation:**

- API documentation: https://platform.openai.com/docs
- API pricing: https://platform.openai.com/pricing
- API data usage and privacy: https://openai.com/policies/api-data-usage-policies
- API security and compliance: https://openai.com/security