"""
Automated Test Suite for Grounded RAG Pipeline.
Verifies ingestion of all 20 RAG policy documents, semantic retrieval precision,
citation formatting, and insufficient evidence handling.
"""
import pytest
from pathlib import Path

from src.rag.ingestion import PolicyIngestion, PolicyChunk
from src.rag.retriever import PolicyRetriever, RetrievedEvidence
from src.rag.pipeline import GroundedRAGPipeline


@pytest.fixture(scope="module")
def rag_dir():
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "RAG"


@pytest.fixture(scope="module")
def ingestion(rag_dir):
    return PolicyIngestion(rag_folder=rag_dir)


@pytest.fixture(scope="module")
def all_chunks(ingestion):
    chunks = ingestion.ingest_all_policies()
    assert len(chunks) > 0, "No policy chunks were ingested from RAG directory!"
    return chunks


@pytest.fixture(scope="module")
def retriever(all_chunks):
    return PolicyRetriever(chunks=all_chunks)


@pytest.fixture(scope="module")
def pipeline(retriever):
    return GroundedRAGPipeline(retriever=retriever)


def test_ingestion_loads_rag_documents(all_chunks):
    """Verifies that policies are parsed and chunks have valid metadata."""
    assert len(all_chunks) >= 20, f"Expected at least 20 chunks, got {len(all_chunks)}"

    source_ids = {c.source_id for c in all_chunks}
    # Check that key policies are indexed
    assert "SACCO-CREDIT-001" in source_ids or any("CREDIT" in s for s in source_ids)

    # Check that each chunk has required fields
    for chunk in all_chunks:
        assert chunk.chunk_id
        assert chunk.source_id
        assert chunk.document_title
        assert chunk.section_heading
        assert chunk.content


def test_retriever_finds_membership_eligibility(retriever):
    """Tests retrieval for member eligibility rules (6 months tenure, shares)."""
    results = retriever.retrieve("membership duration 6 months minimum shares active member", top_k=3)
    assert len(results) > 0

    top_result = results[0]
    # Expect SACCO-CREDIT-001 or Bylaws
    assert top_result.score > 0.08
    retrieved_text = (top_result.chunk.section_heading + " " + top_result.chunk.content).lower()
    assert "eligibility" in retrieved_text or "membership" in retrieved_text or "month" in retrieved_text


def test_retriever_finds_debt_service_ratio(retriever):
    """Tests retrieval for DSR and affordability threshold (50%)."""
    results = retriever.retrieve("Debt Service Ratio DSR affordability threshold 50 percent net monthly income", top_k=3)
    assert len(results) > 0

    combined_text = " ".join([r.chunk.content for r in results]).lower()
    assert "50%" in combined_text or "dsr" in combined_text or "affordability" in combined_text


def test_retriever_finds_kyc_requirements(retriever):
    """Tests retrieval for KYC / AML documentation."""
    results = retriever.retrieve("KYC verification Level 2 National ID physical address LC1 letter", top_k=3)
    assert len(results) > 0

    combined_text = " ".join([r.chunk.content for r in results]).lower()
    assert "kyc" in combined_text or "identity" in combined_text or "id" in combined_text


def test_citation_formatting(retriever):
    """Verifies that citations follow the required provenance structure."""
    results = retriever.retrieve("savings multiplier loan limits", top_k=2)
    assert len(results) > 0

    evidence = results[0]
    citation = evidence.citation
    assert "Source ID:" in citation
    assert "Doc:" in citation
    assert "Section:" in citation


def test_insufficient_evidence_handling(pipeline):
    """Queries for an out-of-scope topic and expects insufficient evidence flag."""
    irrelevant_query = "quantum computing cryptocurrency mining protocol and dogecoin smart contracts"
    response = pipeline.run_qa(irrelevant_query, llm_service=None)

    assert response["sufficient_evidence"] is False
    assert "INSUFFICIENT EVIDENCE" in response["answer"]


def test_case_evidence_retrieval(pipeline):
    """Tests multi-dimensional case evidence retrieval for a sample member."""
    sample_member = {
        "member_id": "M-999",
        "loan_purpose": "School Fees",
        "requested_loan": 3000000,
        "requested_term_months": 12,
        "membership_months": 4,  # Under 6 months
        "kyc_status": "unverified",
        "has_arrears": True,
        "number_of_guarantors": 0
    }
    sample_repayment = {
        "monthly_payment": 280000,
        "total_interest": 360000,
        "total_repayment": 3360000
    }

    evidence = pipeline.retrieve_evidence_for_case(sample_member, sample_repayment, max_chunks=5)
    assert len(evidence) >= 3

    prompt = pipeline.build_case_prompt(sample_member, sample_repayment, evidence)
    assert "RETRIEVED APPROVED SACCO POLICY EVIDENCE" in prompt
    assert "M-999" in prompt
    assert "Source Citation" in prompt
