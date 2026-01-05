"""
document_parser.py

Custom document parser for inquest transcripts that extracts structured metadata
including page numbers, line numbers, speakers, and dates from the transcript format.

The transcript format uses:
- Standalone numbers (1, 2, 3...) to indicate page breaks
- Line numbers at the start of each line (e.g., "5 MR HILLIARD: Sir...")
- Speaker names in format "MR/MS/SIR/LORD NAME:"
- Date headers like "Monday, 1 December 2008"
"""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from llama_index.core import Document
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo


@dataclass
class TranscriptMetadata:
    """Metadata extracted from a transcript chunk."""
    file_name: str
    page_number: int = 1
    line_start: int = 1
    line_end: int = 1
    speaker: Optional[str] = None
    date: Optional[str] = None
    speakers_in_chunk: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for node metadata."""
        return {
            "file_name": self.file_name,
            "page_number": self.page_number,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "speaker": self.speaker,
            "date": self.date,
            "speakers_in_chunk": ", ".join(self.speakers_in_chunk) if self.speakers_in_chunk else None,
            # Formatted citation string for easy reference
            "citation": f"[{self.file_name}, Page {self.page_number}, Lines {self.line_start}-{self.line_end}]"
        }


class TranscriptParser:
    """
    Parser for inquest transcript documents that extracts page/line metadata.
    
    The transcript format:
    ```
    1                           <- Page number (standalone digit)
    1 Monday, 1 December 2008   <- Line 1 with date
    2 (10.00 am)                <- Line 2
    3 Housekeeping              <- Line 3, section header
    4 SIR MICHAEL WRIGHT: Yes   <- Line 4, speaker identified
    5 MR HILLIARD: Sir, just... <- Line 5, new speaker
    
    2                           <- Page 2 starts
    1 MR HILLIARD: Certainly... <- Line 1 of page 2
    ```
    """
    
    # Regex patterns
    PAGE_BREAK_PATTERN = re.compile(r'^(\d+)\s*$')  # Standalone number = page break
    LINE_PATTERN = re.compile(r'^(\d+)\s+(.+)$')    # Line number followed by content
    SPEAKER_PATTERN = re.compile(r'\b(MR|MS|MRS|SIR|LORD|LADY|DR|PROFESSOR)\s+([A-Z][A-Z\-\']+)', re.IGNORECASE)
    DATE_PATTERN = re.compile(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\d+\s+\w+\s+\d{4}', re.IGNORECASE)
    TIME_PATTERN = re.compile(r'\((\d{1,2}\.\d{2}\s*(?:am|pm)?)\)', re.IGNORECASE)
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 128):
        """
        Initialize the transcript parser.
        
        Args:
            chunk_size: Target size for each chunk in characters.
            chunk_overlap: Overlap between chunks to preserve context.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def parse_document(self, document: Document) -> list[TextNode]:
        """
        Parse a transcript document into nodes with metadata.
        
        Args:
            document: LlamaIndex Document object.
            
        Returns:
            List of TextNode objects with extracted metadata.
        """
        file_name = document.metadata.get("file_name", "unknown")
        text = document.text
        
        # Parse the document structure
        parsed_lines = self._parse_lines(text)
        
        # Extract document-level date if present
        doc_date = self._extract_date(text[:500])  # Check first 500 chars
        
        # Create chunks with metadata
        nodes = self._create_chunks(parsed_lines, file_name, doc_date, document.doc_id)
        
        return nodes
    
    def _parse_lines(self, text: str) -> list[dict]:
        """
        Parse text into structured lines with page/line numbers.
        
        Returns list of dicts with keys: page, line, content, speaker
        """
        lines = text.split('\n')
        parsed = []
        current_page = 1
        
        for raw_line in lines:
            raw_line = raw_line.rstrip()
            
            if not raw_line:
                continue
            
            # Check for page break (standalone number)
            page_match = self.PAGE_BREAK_PATTERN.match(raw_line)
            if page_match:
                current_page = int(page_match.group(1))
                continue
            
            # Check for line number prefix
            line_match = self.LINE_PATTERN.match(raw_line)
            if line_match:
                line_num = int(line_match.group(1))
                content = line_match.group(2)
            else:
                # No line number - use sequential or continuation
                line_num = parsed[-1]["line"] + 1 if parsed else 1
                content = raw_line
            
            # Extract speaker if present
            speaker = self._extract_speaker(content)
            
            parsed.append({
                "page": current_page,
                "line": line_num,
                "content": content,
                "speaker": speaker,
                "raw": raw_line
            })
        
        return parsed
    
    def _extract_speaker(self, text: str) -> Optional[str]:
        """Extract speaker name from text like 'MR HILLIARD: ...'"""
        # Look for pattern at start of line or after standard prefixes
        match = self.SPEAKER_PATTERN.search(text[:100])  # Check first 100 chars
        if match:
            title = match.group(1).upper()
            name = match.group(2).upper()
            return f"{title} {name}"
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text like 'Monday, 1 December 2008'"""
        match = self.DATE_PATTERN.search(text)
        return match.group(0) if match else None
    
    def _create_chunks(
        self, 
        parsed_lines: list[dict], 
        file_name: str,
        doc_date: Optional[str],
        doc_id: str
    ) -> list[TextNode]:
        """
        Create text chunks with proper metadata from parsed lines.
        """
        nodes = []
        current_chunk_lines = []
        current_chunk_text = ""
        chunk_start_page = 1
        chunk_start_line = 1
        current_speakers = set()
        
        for i, line_data in enumerate(parsed_lines):
            line_text = line_data["content"]
            
            # Track if adding this line exceeds chunk size
            potential_text = current_chunk_text + "\n" + line_text if current_chunk_text else line_text
            
            if len(potential_text) > self.chunk_size and current_chunk_lines:
                # Create node from current chunk
                node = self._create_node(
                    text=current_chunk_text,
                    file_name=file_name,
                    page=chunk_start_page,
                    line_start=chunk_start_line,
                    line_end=current_chunk_lines[-1]["line"],
                    speakers=list(current_speakers),
                    date=doc_date,
                    doc_id=doc_id,
                    node_index=len(nodes)
                )
                nodes.append(node)
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk_lines) - 3)  # Keep last 3 lines for overlap
                current_chunk_lines = current_chunk_lines[overlap_start:]
                current_chunk_text = "\n".join(l["content"] for l in current_chunk_lines)
                chunk_start_page = current_chunk_lines[0]["page"] if current_chunk_lines else line_data["page"]
                chunk_start_line = current_chunk_lines[0]["line"] if current_chunk_lines else line_data["line"]
                current_speakers = {l["speaker"] for l in current_chunk_lines if l["speaker"]}
            
            # Add line to current chunk
            current_chunk_lines.append(line_data)
            current_chunk_text = current_chunk_text + "\n" + line_text if current_chunk_text else line_text
            
            if not current_chunk_lines[:-1]:  # First line in chunk
                chunk_start_page = line_data["page"]
                chunk_start_line = line_data["line"]
            
            if line_data["speaker"]:
                current_speakers.add(line_data["speaker"])
        
        # Create final node if there's remaining content
        if current_chunk_lines:
            node = self._create_node(
                text=current_chunk_text,
                file_name=file_name,
                page=chunk_start_page,
                line_start=chunk_start_line,
                line_end=current_chunk_lines[-1]["line"],
                speakers=list(current_speakers),
                date=doc_date,
                doc_id=doc_id,
                node_index=len(nodes)
            )
            nodes.append(node)
        
        # Set up node relationships
        for i, node in enumerate(nodes):
            if i > 0:
                node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                    node_id=nodes[i-1].node_id
                )
            if i < len(nodes) - 1:
                node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                    node_id=nodes[i+1].node_id
                )
        
        return nodes
    
    def _create_node(
        self,
        text: str,
        file_name: str,
        page: int,
        line_start: int,
        line_end: int,
        speakers: list[str],
        date: Optional[str],
        doc_id: str,
        node_index: int
    ) -> TextNode:
        """Create a TextNode with full metadata."""
        metadata = TranscriptMetadata(
            file_name=file_name,
            page_number=page,
            line_start=line_start,
            line_end=line_end,
            speaker=speakers[0] if speakers else None,
            date=date,
            speakers_in_chunk=speakers
        )
        
        return TextNode(
            text=text.strip(),
            metadata=metadata.to_dict(),
            excluded_embed_metadata_keys=["citation", "speakers_in_chunk"],
            excluded_llm_metadata_keys=[],  # Include all metadata for LLM context
        )


def parse_all_documents(documents: list[Document], chunk_size: int = 512, chunk_overlap: int = 128) -> list[TextNode]:
    """
    Parse all documents into nodes with transcript metadata.
    
    Args:
        documents: List of LlamaIndex Document objects.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks.
        
    Returns:
        List of TextNode objects with extracted metadata.
    """
    parser = TranscriptParser(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_nodes = []
    
    for doc in documents:
        nodes = parser.parse_document(doc)
        all_nodes.extend(nodes)
        print(f"  Parsed {doc.metadata.get('file_name', 'unknown')}: {len(nodes)} chunks")
    
    return all_nodes


def extract_citation_from_node(node: TextNode) -> str:
    """
    Extract a formatted citation string from a node's metadata.
    
    Args:
        node: TextNode with metadata.
        
    Returns:
        Formatted citation string like "[dec_01.pdf.md, Page 3, Lines 12-15]"
    """
    meta = node.metadata
    file_name = meta.get("file_name", "unknown")
    page = meta.get("page_number", "?")
    line_start = meta.get("line_start", "?")
    line_end = meta.get("line_end", "?")
    
    if line_start == line_end:
        return f"[{file_name}, Page {page}, Line {line_start}]"
    return f"[{file_name}, Page {page}, Lines {line_start}-{line_end}]"


if __name__ == "__main__":
    # Test the parser with a sample document
    from llama_index.core import SimpleDirectoryReader
    
    print("Testing TranscriptParser...")
    
    # Load a single document for testing
    test_dir = Path(__file__).parent / "plain_texts"
    if test_dir.exists():
        reader = SimpleDirectoryReader(str(test_dir), filename_as_id=True)
        docs = reader.load_data()
        
        if docs:
            # Parse first document
            parser = TranscriptParser(chunk_size=512, chunk_overlap=128)
            nodes = parser.parse_document(docs[0])
            
            print(f"\nParsed {docs[0].metadata.get('file_name')}: {len(nodes)} chunks")
            print("\nSample chunks:")
            for i, node in enumerate(nodes[:3]):
                print(f"\n--- Chunk {i+1} ---")
                print(f"Citation: {node.metadata.get('citation')}")
                print(f"Speakers: {node.metadata.get('speakers_in_chunk')}")
                print(f"Date: {node.metadata.get('date')}")
                print(f"Text preview: {node.text[:200]}...")
    else:
        print(f"Test directory not found: {test_dir}")
