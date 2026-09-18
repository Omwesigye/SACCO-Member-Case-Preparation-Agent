"""
Policy loader module for SACCO Member-Case Preparation Agent.
Connects the application to the Grounded RAG Pipeline, indexing all 20 approved
SACCO policy documents in /RAG with semantic retrieval and citation provenance.
"""
from pathlib import Path
import sys

# Ensure repository root is on sys.path
def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "RAG").is_dir():
            return p
    return current.parents[3]

REPO_ROOT = _find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.rag.ingestion import PolicyIngestion
from src.rag.retriever import PolicyRetriever, RetrievedEvidence
from src.rag.pipeline import GroundedRAGPipeline

# Cache singleton instance
_pipeline_instance = None


def get_rag_pipeline() -> GroundedRAGPipeline:
    """Returns singleton Grounded RAG Pipeline."""
    global _pipeline_instance
    if _pipeline_instance is None:
        ingestion = PolicyIngestion(rag_folder=REPO_ROOT / "RAG")
        chunks = ingestion.ingest_all_policies()
        retriever = PolicyRetriever(chunks=chunks)
        _pipeline_instance = GroundedRAGPipeline(retriever=retriever)
    return _pipeline_instance


def retrieve_case_evidence(member: dict, repayment: dict, max_chunks: int = 5):
    """Retrieves relevant policy evidence specifically tailored to a member case."""
    pipeline = get_rag_pipeline()
    return pipeline.retrieve_evidence_for_case(member, repayment, max_chunks=max_chunks)


def retrieve_query_evidence(query: str, top_k: int = 4):
    """Retrieves relevant policy evidence for an arbitrary loan officer question."""
    pipeline = get_rag_pipeline()
    return pipeline.retrieve_evidence_for_query(query, top_k=top_k)


def load_all_policies():
    """
    Backward-compatible fallback loader.
    Loads approved policies formatted with source headers.
    """
    pipeline = get_rag_pipeline()
    # Format all top policy documents
    return pipeline.retriever.format_evidence_pack(
        [RetrievedEvidence(chunk=c, score=1.0) for c in pipeline.retriever.chunks[:10]]
    )