System Architecture
 
![SACCO Member Case Preparation Agent Architectur](https://github.com/Omwesigye/SACCO-Member-Case-Preparation-Agent/blob/f3305d9ed34e756b03e28bea5fa081190edbcc5d/Architecture.png)

The SACCO Member Case Preparation Agent is an Agentic AI component designed to support the Loans Department by assisting loan officers in preparing and understanding member loan cases. The agent does not make credit decisions or perform financial transactions. Instead it acts as an intelligent assistant that retrieves relevant SACCO policies, analyzes authorized member case information, performs illustrative calculations and prepares a structured case for review by human staff.
The architecture consists of the following main components:
1. Agent Orchestrator
 The Agent Orchestrator is the central component responsible for coordinating the activities of the AI agent. It receives a request from a loan officer, interprets the task, determines what information is required, selects the appropriate tools and combines the results into a final case preparation response. This enables the system to perform multiple steps autonomously rather than simply responding to individual questions.
2. Policy Retrieval Tool and Knowledge Base
 The Policy Retrieval Tool allows the agent to access approved SACCO policy documents, procedures, guidelines and other relevant documentation. These documents are stored in a searchable knowledge base and retrieved using a Retrieval Augmented Generation (RAG) approach. This enables the agent to provide explanations and procedural guidance based on the available SACCO policies rather than relying solely on the general knowledge of the language model.
3. Case Data Retrieval Tool
 The Case Data Retrieval Tool provides the agent with the information required to prepare a member's case. During development, this component can use synthetic member records created by the project team. The tool provides only the information required for the requested task and does not allow the agent to modify member records.
4. Loan Schedule Calculator
 The Loan Schedule Calculator is a deterministic tool used to generate illustrative loan repayment schedules. Instead of relying on the language model to perform financial mathematics, the agent sends the required parameters to the calculator, which performs the calculation and returns the results. The agent can then explain the calculated schedule to the loan officer.
5. LLM/Reasoning Engine
 The LLM serves as the reasoning and language component of the agent. It interprets the loan officer's request, reasons over information retrieved from the policy knowledge base and case data, determines which tools are necessary and produces a clear explanation and structured case summary.
6. Case Preparation Output
 The results from the different tools are combined into a structured loan case. The output may include applicable procedures, required documentation, missing information, relevant policy requirements, an illustrative repayment schedule and a summary of the case. The output is clearly marked as prepared for staff review.
7. Human-in-the-Loop Review
 The final component is the human review stage. The prepared case is submitted to the loan officer or other authorized SACCO staff for assessment. The AI does not make the final lending decision. This ensures that responsibility for credit decisions remains with authorized human personnel.
The architecture therefore follows the flow:
Loan Officer Request → Agent Orchestrator → Policy/Data Retrieval & Calculation Tools → LLM Reasoning → Case Preparation → Human Staff Review
The agent is deliberately designed with a restricted action boundary. It can retrieve information, explain policies, identify missing requirements, prepare cases and generate illustrative schedules but it cannot perform credit scoring, loan approval or rejection, loan disbursement, account modification or real financial transactions. This human in the loop design makes the agent suitable for supporting the SACCO's Loans Department while maintaining human accountability and control over financial decisions.
