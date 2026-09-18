"""
Policy Evidence Retriever for SACCO Member-Case Preparation Agent.
Implements vector/TF-IDF semantic similarity search with score thresholding
and standardized citation provenance formatting.
"""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .ingestion import PolicyChunk, PolicyIngestion


@dataclass
class RetrievedEvidence:
    chunk: PolicyChunk
    score: float

    @property
    def citation(self) -> str:
        """Formatted citation for audit and grounding."""
        return (
            f"[Source ID: {self.chunk.source_id} | "
            f"Doc: {self.chunk.document_title} ({self.chunk.version}) | "
            f"Section: {self.chunk.section_heading}]"
        )

    @property
    def short_citation(self) -> str:
        return f"{self.chunk.source_id} ({self.chunk.section_heading})"

    @property
    def relevance_tier(self) -> str:
        if self.score >= 0.20:
            return "HIGH"
        elif self.score >= 0.08:
            return "MEDIUM"
        return "LOW"


class PolicyRetriever:
    """
    Indexes policy chunks and performs semantic similarity retrieval
    to ground case preparation responses in verified policy text.
    """

    def __init__(self, chunks: Optional[List[PolicyChunk]] = None):
        if chunks is None:
            ingestion = PolicyIngestion()
            chunks = ingestion.ingest_all_policies()

        self.chunks: List[PolicyChunk] = chunks
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        if self.chunks:
            self._build_index()

    def _build_index(self):
        """Builds TF-IDF vector matrix over the chunk corpus."""
        corpus = [c.searchable_text for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            stop_words="english"
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        min_score: float = 0.05
    ) -> List[RetrievedEvidence]:
        """
        Retrieves top-k most relevant policy evidence chunks for a query.
        Discards chunks below min_score to avoid retrieving noise.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        clean_query = query.strip()
        if not clean_query:
            return []

        query_vec = self.vectorizer.transform([clean_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top indices sorted descending
        ranked_indices = np.argsort(similarities)[::-1]

        results: List[RetrievedEvidence] = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score < min_score:
                break
            results.append(
                RetrievedEvidence(
                    chunk=self.chunks[idx],
                    score=round(score, 4)
                )
            )
            if len(results) >= top_k:
                break

        return results

    def format_evidence_pack(self, evidence_list: List[RetrievedEvidence]) -> str:
        """
        Formats retrieved evidence into a structured string context
        suitable for LLM prompt injection.
        """
        if not evidence_list:
            return "NO RELEVANT SACCO POLICY EVIDENCE FOUND IN APPROVED CORPUS."

        lines = [
            "=== RETRIEVED APPROVED SACCO POLICY EVIDENCE ===",
            "Instructions: Ground your response strictly in the following evidence.",
            "Each fact or rule cited MUST reference its Source ID and Section.",
            ""
        ]

        for i, ev in enumerate(evidence_list, start=1):
            c = ev.chunk
            lines.append(
                f"--- EVIDENCE ITEM {i} [Relevance: {ev.relevance_tier} | Score: {ev.score:.3f}] ---"
            )
            lines.append(f"Source ID: {c.source_id}")
            lines.append(f"Document Title: {c.document_title}")
            lines.append(f"Version: {c.version} (Effective: {c.effective_date})")
            lines.append(f"Section Heading: {c.section_heading}")
            lines.append(f"Origin/File: {c.file_name}")
            lines.append("Content:")
            lines.append(c.content.strip())
            lines.append("")

        lines.append("=== END OF POLICY EVIDENCE ===")
        return "\n".join(lines)
