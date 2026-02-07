"""
inquestindex.py

Modern RAG pipeline for analyzing inquest documents using:
- Milvus Lite for persistent vector storage
- Groq API (Llama 3.3 70B) for generation
- Cross-encoder reranking for improved retrieval precision
- Citation verification for legal accuracy

Usage:
    python inquestindex.py                    # Run with existing index
    python inquestindex.py --rebuild-index    # Force rebuild the vector index
    python inquestindex.py --verbose          # Enable detailed logging

Requirements:
    - .env file with GROQ_API_KEY (copy from .env.example)
    - Ollama running with 'nomic-embed-text' model for embeddings
    - All .md files to be indexed should be in the 'plain_texts' folder
"""

# Suppress Pydantic warning from llama-index dependencies
# This is a known issue with llama-index using Field(validate_default=True) incorrectly
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

# Fix for Python 3.14 + pymilvus async client initialization
# The AsyncMilvusClient requires an event loop, so we create one before importing
import asyncio
import nest_asyncio
nest_asyncio.apply()

import os
import sys
import argparse
from pathlib import Path

# LlamaIndex core
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings

# Embeddings (local via Ollama - no data sent externally)
from llama_index.embeddings.ollama import OllamaEmbedding

# LLM (Groq API for Llama 3.3 70B, or Ollama for local)
from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama

# Vector store (Milvus Lite - embedded, no Docker)
from llama_index.vector_stores.milvus import MilvusVectorStore

# Reranking for better retrieval precision
from llama_index.core.postprocessor import SentenceTransformerRerank

# Local imports
from config import (
    GROQ_API_KEY, GROQ_MODEL, GROQ_REQUEST_TIMEOUT,
    OLLAMA_EMBEDDING_MODEL, OLLAMA_LLM_MODEL, OLLAMA_LLM_REQUEST_TIMEOUT,
    MILVUS_DB_PATH, MILVUS_COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP,
    RERANK_MODEL, INITIAL_RETRIEVAL_TOP_K, RERANK_TOP_N,
    BASE_INSTRUCTION, ANALYSIS_INSTRUCTION, CITATION_INSTRUCTION,
    INQUESTINDEX_OUTPUTS_DIR,
    validate_config, print_config_summary
)
from document_parser import parse_all_documents
from utils import validate_citations, format_citation_summary, log


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze inquest documents using RAG with Milvus and Groq"
    )
    parser.add_argument(
        '--rebuild-index', '-r',
        action='store_true',
        help='Force rebuild the vector index (otherwise reuses existing)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='Verbose output (default: enabled)'
    )
    parser.add_argument(
        '--quiet',
        action='store_false',
        dest='verbose',
        help='Disable verbose output'
    )
    parser.add_argument(
        '--question', '-q',
        type=int,
        default=None,
        help='Run only a specific question number (1-based)'
    )
    parser.add_argument(
        '--analysis-only', '-a',
        action='store_true',
        help='Run only analysis questions (broader ethical/AI implications)'
    )
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip analysis questions, run only factual evidence questions'
    )
    parser.add_argument(
        '--use-ollama',
        action='store_true',
        help='Use local Ollama LLM (gpt-oss:20b) instead of Groq API'
    )
    return parser.parse_args()


def setup_llm_and_embeddings(verbose: bool = False, use_ollama: bool = False):
    """
    Configure LLM (Groq or Ollama) and embeddings (Ollama) for the pipeline.
    
    Embeddings are computed locally via Ollama to avoid sending document
    content to external APIs. LLM can be either Groq API or local Ollama.
    
    Args:
        verbose: Enable detailed logging.
        use_ollama: If True, use local Ollama LLM instead of Groq API.
    """
    log("Setting up LLM and embeddings...", verbose)
    
    if use_ollama:
        # Local Ollama LLM (gpt-oss:20b)
        llm = Ollama(
            model=OLLAMA_LLM_MODEL,
            request_timeout=OLLAMA_LLM_REQUEST_TIMEOUT
        )
        log(f"  LLM: Ollama {OLLAMA_LLM_MODEL} (local)", verbose)
    else:
        # Groq LLM for generation (Llama 3.3 70B)
        llm = Groq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            request_timeout=GROQ_REQUEST_TIMEOUT
        )
        log(f"  LLM: Groq {GROQ_MODEL}", verbose)
    
    Settings.llm = llm
    
    # Local embeddings via Ollama (no data sent externally)
    # Explicitly set base_url to avoid stale port issues when Ollama restarts
    Settings.embed_model = OllamaEmbedding(
        model_name=OLLAMA_EMBEDDING_MODEL,
        base_url="http://localhost:11434",
        embed_batch_size=32  # Process 32 chunks per batch
    )
    
    log(f"  Embeddings: Ollama {OLLAMA_EMBEDDING_MODEL} (local)", verbose)


def build_or_load_index(rebuild: bool = False, verbose: bool = False) -> VectorStoreIndex:
    """
    Build a new vector index or load existing one from Milvus.
    
    Args:
        rebuild: If True, force rebuild even if index exists.
        verbose: Enable detailed logging.
        
    Returns:
        VectorStoreIndex ready for querying.
    """
    log("Setting up vector store...", verbose)
    
    # Check if we need to rebuild
    db_exists = Path(MILVUS_DB_PATH).exists()
    
    if db_exists and not rebuild:
        log(f"  Loading existing index from {MILVUS_DB_PATH}", verbose)
        
        # Connect to existing Milvus Lite database
        # Note: pymilvus 2.6+ requires an event loop for async client initialization
        async def load_vector_store():
            return MilvusVectorStore(
                uri=MILVUS_DB_PATH,
                collection_name=MILVUS_COLLECTION_NAME,
                dim=768,  # nomic-embed-text dimension
                overwrite=False
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            vector_store = loop.run_until_complete(load_vector_store())
        finally:
            loop.close()
        
        # Create index from existing store
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        log("  ✅ Loaded existing index", verbose)
        return index
    
    # Build new index
    log("  Building new index from documents...", verbose)
    
    # Load documents
    documents = SimpleDirectoryReader("plain_texts", filename_as_id=True).load_data()
    log(f"  Loaded {len(documents)} documents", verbose)
    
    # Parse documents with transcript metadata extraction
    log("  Parsing transcripts for page/line metadata...", verbose)
    nodes = parse_all_documents(
        documents, 
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    log(f"  Created {len(nodes)} chunks with metadata", verbose)
    
    # Create Milvus Lite vector store
    # Note: pymilvus 2.6+ requires an event loop for async client initialization
    async def create_vector_store():
        return MilvusVectorStore(
            uri=MILVUS_DB_PATH,
            collection_name=MILVUS_COLLECTION_NAME,
            dim=768,  # nomic-embed-text dimension
            overwrite=True  # Fresh start
        )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        vector_store = loop.run_until_complete(create_vector_store())
    finally:
        loop.close()
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Calculate batch information for progress display
    embed_batch_size = Settings.embed_model.embed_batch_size
    total_batches = (len(nodes) + embed_batch_size - 1) // embed_batch_size
    log(f"  Generating embeddings: {len(nodes)} chunks in {total_batches} batches (batch size: {embed_batch_size})", verbose)
    
    # Manually embed nodes in batches with progress display
    embed_model = Settings.embed_model
    for batch_idx in range(total_batches):
        start_idx = batch_idx * embed_batch_size
        end_idx = min(start_idx + embed_batch_size, len(nodes))
        batch_nodes = nodes[start_idx:end_idx]
        
        # Get text content from nodes for embedding
        texts = [node.get_content(metadata_mode="all") for node in batch_nodes]
        
        # Generate embeddings for this batch
        embeddings = embed_model.get_text_embedding_batch(texts)
        
        # Assign embeddings to nodes
        for node, embedding in zip(batch_nodes, embeddings):
            node.embedding = embedding
        
        # Display progress bar (clears entire line to prevent wrapping issues)
        progress = (batch_idx + 1) / total_batches
        bar_width = 30
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        percent = progress * 100
        status = f"  Embeddings: [{bar}] {percent:5.1f}% ({batch_idx + 1}/{total_batches})"
        sys.stdout.write(f"\r\033[K{status}")
        sys.stdout.flush()
    
    print()  # Newline after progress complete
    
    # Build index from pre-embedded nodes
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        show_progress=False  # Disable default progress since we already embedded
    )
    
    log(f"  ✅ Index built and saved to {MILVUS_DB_PATH}", verbose)
    return index


def create_query_engine(index: VectorStoreIndex, verbose: bool = False):
    """
    Create a query engine with reranking for improved precision.
    
    Args:
        index: The vector index to query.
        verbose: Enable detailed logging.
        
    Returns:
        Query engine configured with reranking.
    """
    log("Creating query engine with reranking...", verbose)
    
    # Cross-encoder reranker for better precision
    reranker = SentenceTransformerRerank(
        model=RERANK_MODEL,
        top_n=RERANK_TOP_N
    )
    
    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=INITIAL_RETRIEVAL_TOP_K,
        node_postprocessors=[reranker],
        response_mode="tree_summarize"
    )
    
    log(f"  Retrieval: Top-{INITIAL_RETRIEVAL_TOP_K} → Rerank to Top-{RERANK_TOP_N}", verbose)
    return query_engine


# ============================================================================
# Questions for Analysis
# ============================================================================

EVIDENCE_QUESTIONS = [
    (
        "List all issues or concerns in the provided documents related to the following categories. "
        "For each, provide the relevant quote with page and line citations:\n"
        "1. CCTV or video footage (missing, unavailable, technical faults, not preserved)\n"
        "2. Audio/video recording of briefings, control room activity, or communications (missing, not made, not preserved)\n"
        "3. Telephone or radio records (missing, destroyed, unavailable)\n"
        "4. Handling, alteration, or overwriting of notes, statements, or logs (including collaboration on statements, overwritten notes, or logs not continued)\n"
        "5. Prioritization or failure to use available evidence (e.g., photographs, intelligence, or imagery not accessed or used)\n"
        "For each instance, cite the specific page and line numbers."
    ),
    (
        "Extract and list, in as much detail as possible, every instance in the provided documents where police evidence, statements, or procedures are described as dishonest, unreliable, inaccurate, incomplete, misleading, or otherwise questioned. "
        "For each instance, provide the relevant quote or passage from the documents, and specify the context (e.g., conferring on accounts, alteration of logs, communications failures, evidence handling, expert witness reliability, etc.). "
        "Organize your answer by theme (e.g., Conferring on Accounts, Surveillance Logs, Communications, Evidence Handling, Expert Witnesses, etc.), and use bullet points for clarity. "
        "Include both explicit allegations and any concerns, criticisms, or recommendations related to the reliability or accuracy of police evidence or procedures."
    ),
    (
        "For each theme above, expand with all subpoints, criticisms, and recommendations. "
        "Include specific page and line references for each point."
    )
]

ANALYSIS_QUESTIONS = [
    (
        "How might using AI/NLP to summarize and interrogate inquest documents affect the speed and quality of legal analysis? "
        "Provide specific examples of potential time savings and discuss how AI's strengths and weaknesses in understanding legal nuances "
        "might impact quality. Compare to traditional manual methods. Cite relevant document excerpts if applicable."
    ),
    (
        "Can AI help detect inconsistencies or possible evidence tampering in inquest documents? "
        "Detail specific methods or algorithms for detection, provide examples from the documents if possible, "
        "and critically evaluate limitations including risks of false positives or negatives."
    ),
    (
        "How could the use of AI in inquests affect the balance of power between families, police, and legal teams? "
        "Analyze scenarios where AI might empower or disadvantage each party, discuss data access and algorithmic bias, "
        "and suggest safeguards to ensure fairness."
    ),
    (
        "What are the transparency and accountability challenges when using AI to process legal evidence? "
        "Explore the opacity of AI decision-making, risks of biased training data, and potential erosion of human oversight. "
        "Propose detailed measures to address these challenges."
    ),
    (
        "In what other ways could AI be used in inquests beyond evidence review and summarization? "
        "Brainstorm innovative applications such as predictive analytics, real-time assistance during hearings, "
        "or public engagement tools. Critically assess feasibility and ethical implications of each idea."
    ),
]


def run_query(
    query_engine, 
    question: str, 
    instruction: str,
    verbose: bool = False
) -> tuple[str, list, list]:
    """
    Run a query and validate citations in the response.
    
    Args:
        query_engine: The configured query engine.
        question: The question to ask.
        instruction: The instruction prefix (citation requirements, etc.)
        verbose: Enable detailed logging.
        
    Returns:
        Tuple of (response_text, valid_citations, missing_citations)
    """
    full_prompt = instruction + question
    
    try:
        response = query_engine.query(full_prompt)
        response_text = str(response)
        
        # Get source nodes for citation validation
        source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
        
        # Validate citations
        valid, missing = validate_citations(response_text, source_nodes, verbose=verbose)
        
        return response_text, valid, missing
        
    except Exception as e:
        log(f"Error running query: {e}", verbose=True)
        return f"Error: {e}", [], []


def main():
    """Main entry point for the RAG pipeline."""
    args = parse_args()
    
    # Validate configuration
    print_config_summary(use_ollama=args.use_ollama)
    issues = validate_config(use_ollama=args.use_ollama)
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before continuing.")
        sys.exit(1)
    
    # Setup LLM and embeddings
    setup_llm_and_embeddings(verbose=args.verbose, use_ollama=args.use_ollama)
    
    # Build or load index
    index = build_or_load_index(rebuild=args.rebuild_index, verbose=args.verbose)
    
    # Create query engine with reranking
    query_engine = create_query_engine(index, verbose=args.verbose)
    
    # Ensure output directory exists
    os.makedirs(INQUESTINDEX_OUTPUTS_DIR, exist_ok=True)
    
    # Run evidence questions (unless --analysis-only)
    if not args.analysis_only:
        print("\n" + "=" * 60)
        print("EVIDENCE ANALYSIS QUESTIONS")
        print("=" * 60)
        
        for i, question in enumerate(EVIDENCE_QUESTIONS, 1):
            # Skip if specific question requested and this isn't it
            if args.question and args.question != i:
                continue
                
            print(f"\n--- Question {i}/{len(EVIDENCE_QUESTIONS)} ---")
            print(f"Q: {question[:100]}...")
            
            response_text, valid, missing = run_query(
                query_engine, question, BASE_INSTRUCTION, verbose=args.verbose
            )
            
            # Format output with citation summary
            output = f"QUESTION: {question}\n\nRESPONSE:\n{response_text}"
            output += format_citation_summary(valid, missing)
            
            # Save to file
            output_path = INQUESTINDEX_OUTPUTS_DIR / f"question_{i}.txt"
            with open(output_path, "w") as f:
                f.write(output)
            
            print(f"\nA: {response_text[:500]}...")
            print(f"\n📄 Saved to: {output_path}")
    
    # Run analysis questions (unless --skip-analysis)
    if not args.skip_analysis:
        print("\n" + "=" * 60)
        print("AI/ETHICS ANALYSIS QUESTIONS")
        print("=" * 60)
        
        for i, question in enumerate(ANALYSIS_QUESTIONS, 1):
            # Skip if specific question requested and this isn't it
            if args.question and args.question != i:
                continue
                
            print(f"\n--- Analysis Question {i}/{len(ANALYSIS_QUESTIONS)} ---")
            print(f"Q: {question[:100]}...")
            
            response_text, valid, missing = run_query(
                query_engine, question, ANALYSIS_INSTRUCTION, verbose=args.verbose
            )
            
            # Format output with citation summary
            output = f"QUESTION: {question}\n\nRESPONSE:\n{response_text}"
            output += format_citation_summary(valid, missing)
            
            # Save to file
            output_path = INQUESTINDEX_OUTPUTS_DIR / f"analysis_question_{i}.txt"
            with open(output_path, "w") as f:
                f.write(output)
            
            print(f"\nA: {response_text[:500]}...")
            print(f"\n📄 Saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print(f"📁 Results saved to: {INQUESTINDEX_OUTPUTS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
