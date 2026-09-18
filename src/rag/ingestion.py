"""
Document Ingestion and Semantic Section-Aware Chunking for SACCO Policy Documents.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re
import yaml


@dataclass
class PolicyChunk:
    chunk_id: str
    source_id: str
    document_title: str
    document_type: str
    version: str
    effective_date: str
    file_name: str
    section_heading: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def citation_label(self) -> str:
        """Returns a standardized citation label."""
        return f"[{self.source_id} | {self.document_title} ({self.version}) | {self.section_heading}]"

    @property
    def searchable_text(self) -> str:
        """Text used for embedding and indexing."""
        return f"{self.document_title} {self.section_heading}\n{self.content}"


class PolicyIngestion:
    """
    Ingests policy documents from the RAG knowledge corpus,
    extracts YAML metadata, and chunks documents by logical sections.
    """

    def __init__(self, rag_folder: Optional[Path] = None):
        if rag_folder is None:
            # Search upwards for the repository root containing RAG
            current = Path(__file__).resolve()
            found = None
            for parent in current.parents:
                if (parent / "RAG").is_dir():
                    found = parent / "RAG"
                    break
            self.rag_folder = found if found else current.parents[2] / "RAG"
        else:
            self.rag_folder = Path(rag_folder)

    def parse_markdown_file(self, file_path: Path) -> List[PolicyChunk]:
        """
        Parses a single markdown policy file, extracts frontmatter,
        and splits body text into section-level chunks.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"Warning: Failed to read {file_path}: {e}")
            return []

        # Parse YAML frontmatter if present
        metadata: Dict[str, str] = {}
        body = raw_text

        if raw_text.startswith("---"):
            parts = raw_text.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body = parts[2]
                try:
                    metadata = yaml.safe_load(frontmatter_text) or {}
                except Exception as e:
                    print(f"Warning: Could not parse frontmatter for {file_path.name}: {e}")

        source_id = str(metadata.get("source_id", file_path.stem.upper()))
        title = str(metadata.get("title", file_path.stem.replace("_", " ").title()))
        doc_type = str(metadata.get("document_type", "Policy Document"))
        version = str(metadata.get("version", "v1.0"))
        effective_date = str(metadata.get("effective_date", "2026-02-01"))

        # Chunk the body by markdown headers (## or ###)
        chunks: List[PolicyChunk] = []
        # Pattern to split by H1/H2/H3 headers
        header_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
        splits = header_pattern.split(body)

        current_heading = "General"
        # The first element before any header
        intro_content = splits[0].strip()
        chunk_counter = 1

        if intro_content and len(intro_content) > 50:
            chunk_id = f"{source_id}_CHK_{chunk_counter:03d}"
            chunks.append(
                PolicyChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    document_title=title,
                    document_type=doc_type,
                    version=version,
                    effective_date=effective_date,
                    file_name=file_path.name,
                    section_heading=current_heading,
                    content=intro_content,
                    metadata=metadata
                )
            )
            chunk_counter += 1

        # Process pairs of (header, content)
        for i in range(1, len(splits), 2):
            heading_line = splits[i].strip()
            # Clean heading: remove '#' markers
            clean_heading = re.sub(r"^#+\s*", "", heading_line).strip()
            section_content = splits[i+1].strip() if i+1 < len(splits) else ""

            if not section_content:
                continue

            chunk_id = f"{source_id}_CHK_{chunk_counter:03d}"
            chunks.append(
                PolicyChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    document_title=title,
                    document_type=doc_type,
                    version=version,
                    effective_date=effective_date,
                    file_name=file_path.name,
                    section_heading=clean_heading,
                    content=section_content,
                    metadata=metadata
                )
            )
            chunk_counter += 1

        return chunks

    def ingest_all_policies(self) -> List[PolicyChunk]:
        """
        Scans RAG folder and parses all approved markdown policy files
        (excluding meta documentation like Rag.md, architecture images, etc.).
        """
        all_chunks: List[PolicyChunk] = []
        if not self.rag_folder.exists():
            print(f"Warning: RAG folder not found at {self.rag_folder}")
            return all_chunks

        # Sort files to ensure deterministic ordering
        md_files = sorted(self.rag_folder.glob("*.md"))

        # Meta files to exclude from policy knowledge corpus
        excluded_files = {"rag.md", "source_register.md"}

        for file_path in md_files:
            if file_path.name.lower() in excluded_files:
                continue

            file_chunks = self.parse_markdown_file(file_path)
            all_chunks.extend(file_chunks)

        return all_chunks
