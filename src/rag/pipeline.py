"""
Grounded RAG Pipeline for SACCO Member-Case Preparation Agent.
Orchestrates policy retrieval, evidence synthesis, grounded prompt formulation,
and provenance attribution.
"""
from typing import Callable, Dict, List, Optional
import json

from .ingestion import PolicyIngestion
from .retriever import PolicyRetriever, RetrievedEvidence


class GroundedRAGPipeline:
    """
    End-to-end Grounded RAG Pipeline.
    Retrieves verified policy clauses from the 20 approved SACCO documents
    and constructs grounded contexts with explicit provenance citations.
    """

    def __init__(self, retriever: Optional[PolicyRetriever] = None):
        if retriever is None:
            ingestion = PolicyIngestion()
            chunks = ingestion.ingest_all_policies()
            retriever = PolicyRetriever(chunks)
        self.retriever = retriever

    def retrieve_evidence_for_query(
        self,
        query: str,
        top_k: int = 4,
        min_score: float = 0.05
    ) -> List[RetrievedEvidence]:
        """Retrieves policy clauses for a specific question."""
        return self.retriever.retrieve(query=query, top_k=top_k, min_score=min_score)

    def retrieve_evidence_for_case(
        self,
        member: Dict,
        repayment: Dict,
        max_chunks: int = 6
    ) -> List[RetrievedEvidence]:
        """
        Retrieves targeted policy evidence across multiple dimensions
        relevant to the member case:
        - Eligibility & membership tenure
        - KYC & documentation
        - Exposure, savings multiplier, & affordability / DSR
        - Guarantor & collateral security
        - Delinquency / arrears rules
        """
        loan_type = member.get("loan_purpose", "general")
        term = member.get("requested_term_months", 12)
        amount = member.get("requested_loan", 0)

        # Multi-query retrieval covering core appraisal dimensions
        queries = [
            f"Borrower eligibility membership duration 6 months savings requirement shares {loan_type}",
            "Level 2 KYC verification National ID physical residential address LC1 letter",
            "Debt Service Ratio DSR affordability threshold 50 percent net monthly income",
            "Savings exposure multiplier 3 times 4 times collateral guarantor requirements",
            "Arrears delinquency default policy non performing loan 12 months"
        ]

        collected_chunks: Dict[str, RetrievedEvidence] = {}

        for q in queries:
            results = self.retriever.retrieve(q, top_k=2, min_score=0.08)
            for ev in results:
                # Deduplicate by chunk_id
                cid = ev.chunk.chunk_id
                if cid not in collected_chunks or ev.score > collected_chunks[cid].score:
                    collected_chunks[cid] = ev

        # Sort all unique collected chunks by relevance score descending
        sorted_evidence = sorted(
            collected_chunks.values(),
            key=lambda x: x.score,
            reverse=True
        )

        return sorted_evidence[:max_chunks]

    def build_qa_prompt(
        self,
        question: str,
        evidence: List[RetrievedEvidence]
    ) -> str:
        """Constructs a grounded question-answering prompt."""
        evidence_context = self.retriever.format_evidence_pack(evidence)

        prompt = f"""You are a SACCO Member-Case Preparation Assistant supporting the Loans Department.

Your task is to answer the loan officer's question strictly using the approved SACCO policy evidence provided below.

GROUNDING & CITATION RULES:
1. Base your answer ONLY on the provided SACCO policy evidence.
2. For EVERY policy rule, requirement, or parameter you state, cite the exact source using this format:
   [Source ID: <id> | <document_title> | Section: <section_heading>]
3. If the provided evidence does NOT contain sufficient information to answer the question or specific parts of it, explicitly state:
   "INSUFFICIENT SACCO POLICY EVIDENCE: The approved knowledge base does not contain guidance on [specific item]."
4. Never invent SACCO policies, loan thresholds, interest rates, or penalties not present in the retrieved evidence.
5. Do NOT make or recommend loan approvals, rejections, or credit decisions.

{evidence_context}

LOAN OFFICER QUESTION:
{question}

Provide your grounded answer with citations below:
"""
        return prompt

    def build_case_prompt(
        self,
        member: Dict,
        repayment: Dict,
        evidence: List[RetrievedEvidence]
    ) -> str:
        """
        Builds a comprehensive grounded case-brief prompt with
        retrieved policy evidence injected.
        """
        evidence_context = self.retriever.format_evidence_pack(evidence)
        member_json = json.dumps(member, indent=2)
        repayment_json = json.dumps(repayment, indent=2)

        prompt = f"""You are a SACCO Member-Case Preparation Assistant supporting the Loans Department.
Your responsibility is to organize the member case and evaluate it against approved SACCO policy evidence for human staff review.

ROLE AND DECISION BOUNDARY:
- You are an assistant preparing information for human review only.
- You must NEVER approve, reject, disburse, or recommend a loan decision.
- You must clearly label all calculations as illustrative.

GROUNDING RULES:
1. In the "Evaluation Against Policy" section, evaluate each applicable requirement.
2. For each evaluation point, MUST provide:
   - Rule evaluated
   - Source Citation: [Source ID: <id> | <document_title> | Section: <section_heading>]
   - Member Evidence: verified value from member record
   - Result: PASS / FAIL / PENDING_EVIDENCE / EXCEPTION_REQUIRED
   - Explanation
3. If a policy requirement cannot be verified from the retrieved evidence, record the result as PENDING_EVIDENCE with a note indicating insufficient policy context.
4. Do NOT invent policies or member facts.

{evidence_context}

MEMBER RECORD (SYNTHETIC):
{member_json}

DETERMINISTIC CALCULATOR RESULT:
{repayment_json}

OUTPUT STRUCTURE:
Produce your case brief using this exact format:

Case Preparation Summary
- Member / Case ID: [Member ID]
- Loan Purpose: [Purpose]
- Requested Amount: [Amount]
- Requested Term: [Term]

Policy Evaluation Register
[For each requirement, evaluate with result and mandatory Source Citation: Source ID + Section]

Required Documentation & KYC Checklist
[List required items with citations and indicate whether member provided them]

Affordability & Illustrative Repayment
[Summarize deterministic calculation, labeling strictly as illustrative and not a loan offer]

Issues Requiring Staff Attention
[Inconsistencies, policy failures, missing items, or exceptions requiring Credit Committee review]

Staff Review Status
Prepared for human staff review only. The AI assistant does not make credit decisions.
"""
        return prompt

    def run_qa(
        self,
        question: str,
        llm_service: Optional[Callable[[str], str]] = None,
        top_k: int = 4
    ) -> Dict:
        """
        Executes end-to-end grounded question answering:
        1. Retrieves policy evidence
        2. Checks sufficiency
        3. Formulates prompt
        4. Calls LLM (or generates grounded synthesis)
        5. Returns response and citations
        """
        evidence = self.retrieve_evidence_for_query(question, top_k=top_k)

        if not evidence or evidence[0].score < 0.045:
            return {
                "answer": (
                    "**INSUFFICIENT EVIDENCE:** The SACCO knowledge base does not contain "
                    f"sufficient approved policy guidance to answer: '{question}'. "
                    "Per SACCO governance rules, the assistant will not speculate on unverified policies."
                ),
                "evidence": evidence,
                "citations": [],
                "sufficient_evidence": False
            }

        prompt = self.build_qa_prompt(question, evidence)

        if llm_service:
            answer = llm_service(prompt)
        else:
            # Fallback deterministic grounded synthesis if no LLM callable supplied
            citations = [ev.citation for ev in evidence]
            top_ev = evidence[0]
            answer = (
                f"Based on **{top_ev.chunk.document_title}** ({top_ev.chunk.version}), "
                f"Section '{top_ev.chunk.section_heading}' {top_ev.citation}:\n\n"
                f"{top_ev.chunk.content[:400]}...\n\n"
                f"*Note: Prepared for loan officer guidance. Refer to cited document for complete text.*"
            )

        citations = [ev.citation for ev in evidence]
        return {
            "answer": answer,
            "evidence": evidence,
            "citations": citations,
            "sufficient_evidence": True,
            "prompt": prompt
        }
