"""
config.py

Centralized configuration for the Inquest AI document analysis pipeline.
All settings for vector store, LLM, chunking, and rate limiting are defined here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Project Paths
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
PLAIN_TEXTS_DIR = PROJECT_ROOT / "plain_texts"
DOWNLOADS_DIR = PROJECT_ROOT / "downloads"
INQUESTINDEX_OUTPUTS_DIR = PROJECT_ROOT / "inquestindex_outputs"
SCENARIO_OUTPUTS_DIR = PROJECT_ROOT / "scenario_outputs"
SUMMARIES_DIR = PROJECT_ROOT / "summaries"

# ============================================================================
# Milvus Vector Store Configuration (Milvus Lite - embedded, no Docker)
# ============================================================================

DATABASE_DIR = PROJECT_ROOT / "database"
MILVUS_DB_PATH = str(DATABASE_DIR / "milvus_inquest.db")
MILVUS_COLLECTION_NAME = "inquest_docs"

# ============================================================================
# Chunking Configuration
# ============================================================================

# Chunk size in tokens/characters for document splitting
CHUNK_SIZE = 512

# Overlap between chunks to preserve context at boundaries
CHUNK_OVERLAP = 128

# ============================================================================
# LLM Configuration
# ============================================================================

# Groq API (Llama 3.3 70B for generation)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_REQUEST_TIMEOUT = 120.0  # seconds

# Ollama (local embeddings - no data sent externally)
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

# Ollama LLM (optional local LLM instead of Groq)
OLLAMA_LLM_MODEL = "qwen3:4b-thinking-2507-q4_K_M"
OLLAMA_LLM_REQUEST_TIMEOUT = 300.0  # seconds (longer timeout for local inference)

# ============================================================================
# Reranking Configuration
# ============================================================================

# Cross-encoder model for reranking retrieved chunks
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Number of chunks to retrieve initially before reranking
INITIAL_RETRIEVAL_TOP_K = 25

# Number of chunks to keep after reranking
RERANK_TOP_N = 8

# ============================================================================
# Rate Limiting (Groq Free Tier: 30 requests/minute)
# ============================================================================

# Delay between API calls in seconds
RATE_LIMIT_DELAY = 2.0

# Maximum retries for rate limit errors
MAX_RETRIES = 3

# Exponential backoff base (seconds)
BACKOFF_BASE = 2.0

# ============================================================================
# Citation Verification
# ============================================================================

# Whether to show warnings for citations not found in sources
WARN_ON_MISSING_CITATIONS = True

# ============================================================================
# Prompts and Instructions
# ============================================================================

# Base instruction to reduce hallucination
ANTI_HALLUCINATION_INSTRUCTION = (
    "Instructions: Only answer using information found in the provided documents. "
    "If the answer is not present, say 'Not found in the documents.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective."
)

# Citation requirement for legal accuracy
CITATION_INSTRUCTION = (
    "You MUST cite specific page and line numbers for every factual claim using this format: "
    "[Page X, Lines Y-Z] or [Page X, Line Y]. "
    "Example: 'Commander Stewart confirmed the timeline [Page 4, Lines 12-15].' "
    "If you cannot find a specific reference, state 'Reference not located in provided excerpts.'"
)

# Combined instruction for all queries
BASE_INSTRUCTION = f"{ANTI_HALLUCINATION_INSTRUCTION}\n\n{CITATION_INSTRUCTION}\n\n"

# Analysis instruction (allows broader reasoning)
ANALYSIS_INSTRUCTION = (
    "You are an expert in law, technology, and ethics. "
    "Reflect on the implications of using AI/NLP in the context of inquests like those described in the documents. "
    "You may use your general knowledge as well as any relevant context from the documents. "
    "Be critical, balanced, and cite examples where possible.\n\n"
    f"{CITATION_INSTRUCTION}\n\n"
)

# ============================================================================
# Utility Functions
# ============================================================================

def validate_config(use_ollama: bool = False) -> list[str]:
    """
    Validate the configuration and return a list of warnings/errors.
    
    Args:
        use_ollama: If True, skip Groq API key validation.
    
    Returns:
        List of warning/error messages. Empty list if all is valid.
    """
    issues = []
    
    if not use_ollama and (not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here"):
        issues.append(
            "⚠️  GROQ_API_KEY not set. Copy .env.example to .env and add your key. "
            "Get a free key at: https://console.groq.com/keys"
        )
    
    if not PLAIN_TEXTS_DIR.exists():
        issues.append(f"⚠️  plain_texts directory not found at: {PLAIN_TEXTS_DIR}")
    
    return issues


def print_config_summary(use_ollama: bool = False):
    """
    Print a summary of the current configuration.
    
    Args:
        use_ollama: If True, show Ollama LLM instead of Groq.
    """
    print("\n" + "=" * 60)
    print("INQUEST AI CONFIGURATION")
    print("=" * 60)
    print(f"Vector Store:    Milvus Lite @ {MILVUS_DB_PATH}")
    print(f"Collection:      {MILVUS_COLLECTION_NAME}")
    if use_ollama:
        print(f"LLM:             Ollama {OLLAMA_LLM_MODEL} (local)")
    else:
        print(f"LLM:             Groq {GROQ_MODEL}")
    print(f"Embeddings:      Ollama {OLLAMA_EMBEDDING_MODEL} (local)")
    print(f"Reranker:        {RERANK_MODEL}")
    print(f"Chunk Size:      {CHUNK_SIZE} (overlap: {CHUNK_OVERLAP})")
    print(f"Retrieval:       Top-{INITIAL_RETRIEVAL_TOP_K} → Rerank to Top-{RERANK_TOP_N}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Quick config validation when run directly
    print_config_summary()
    issues = validate_config()
    if issues:
        print("Configuration Issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ Configuration valid!")
