"""
Shared utilities for the Inquest AI document analysis pipeline.

This module provides common functions for:
- Querying LLMs (Groq API or local Ollama)
- Iterating over documents in a directory
- Generating consistent output paths
- Setting up command-line argument parsing
- Citation validation for legal accuracy
- Rate limiting for API calls
- Verbose logging
"""

import os
import re
import time
import argparse
from typing import Generator, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import ollama
except ImportError:
    ollama = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# Import config if available
try:
    from config import (
        GROQ_API_KEY, GROQ_MODEL, RATE_LIMIT_DELAY, 
        MAX_RETRIES, BACKOFF_BASE, WARN_ON_MISSING_CITATIONS
    )
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    RATE_LIMIT_DELAY = 2.0
    MAX_RETRIES = 3
    BACKOFF_BASE = 2.0
    WARN_ON_MISSING_CITATIONS = True

# ============================================================================
# Security Constants
# ============================================================================

# Maximum allowed input lengths to prevent resource exhaustion attacks
MAX_PROMPT_LENGTH = 10000  # characters
MAX_CONTEXT_LENGTH = 100000  # characters (~25k tokens)
MAX_COMBINED_LENGTH = 120000  # characters

# Patterns that could indicate prompt injection attempts
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions?",
    r"disregard\s+(previous|above|all)\s+instructions?",
    r"forget\s+(previous|above|all)\s+instructions?",
    r"new\s+instructions?\s*:",
    r"system\s*:\s*you\s+are",
]


def sanitize_llm_input(
    text: str,
    max_length: int,
    field_name: str = "input",
    check_injection: bool = True,
    verbose: bool = False
) -> tuple[str, list[str]]:
    """
    Sanitize and validate input text for LLM queries.
    
    Args:
        text: The input text to sanitize.
        max_length: Maximum allowed length in characters.
        field_name: Name of the field for error messages.
        check_injection: Whether to check for prompt injection patterns.
        verbose: Whether to log warnings.
        
    Returns:
        Tuple of (sanitized_text, list_of_warnings).
    """
    warnings = []
    
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
        warnings.append(f"{field_name} was not a string, converted")
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
        warning = f"{field_name} truncated from {len(text)} to {max_length} characters"
        warnings.append(warning)
        log(f"Security Warning: {warning}", verbose)
    
    # Check for potential prompt injection patterns
    if check_injection:
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warning = f"Potential prompt injection detected in {field_name}"
                warnings.append(warning)
                log(f"Security Warning: {warning}", verbose)
                break
    
    return text, warnings


def log(message: str, verbose: bool = True) -> None:
    """
    Print a message if verbose mode is enabled.

    Args:
        message: The message to print.
        verbose: Whether to print the message.
    """
    if verbose:
        print(message)


def ask_llama(
    prompt: str,
    context: str,
    model: str = "gpt-oss:20b",
    system_prompt: str = "You are an expert legal assistant.",
    verbose: bool = False
) -> Optional[str]:
    """
    Query the local Llama model using Ollama with a given prompt and context.

    Args:
        prompt: The prompt or question to ask the model.
        context: The context or document text to provide to the model.
        model: The Ollama model to use (default: gpt-oss:20b).
        system_prompt: The system prompt for the model.
        verbose: Whether to print progress messages.

    Returns:
        The model's response, or None if an error occurred.
    """
    if ollama is None:
        log("Error: ollama package is not installed. Run: pip install ollama", verbose=True)
        return None

    # Security: Validate and sanitize inputs
    prompt, prompt_warnings = sanitize_llm_input(
        prompt, MAX_PROMPT_LENGTH, "prompt", check_injection=True, verbose=verbose
    )
    context, context_warnings = sanitize_llm_input(
        context, MAX_CONTEXT_LENGTH, "context", check_injection=False, verbose=verbose
    )
    
    # Check combined length
    combined_length = len(prompt) + len(context)
    if combined_length > MAX_COMBINED_LENGTH:
        log(f"Security Warning: Combined input too large ({combined_length} chars), truncating context", verbose)
        allowed_context = MAX_COMBINED_LENGTH - len(prompt)
        context = context[:allowed_context]

    try:
        log(f"Querying {model}...", verbose)
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {prompt}"}
            ]
        )
        return response['message']['content']
    except ConnectionError:
        log("Error: Could not connect to Ollama. Is it running?", verbose=True)
        return None
    except Exception as e:
        log(f"Error querying {model}: {e}", verbose=True)
        return None


def iterate_documents(
    input_dir: str,
    extension: str = ".md",
    verbose: bool = False
) -> Generator[tuple[str, str], None, None]:
    """
    Iterate over documents in a directory with the given extension.

    Args:
        input_dir: The directory to iterate over.
        extension: The file extension to filter by (default: .md).
        verbose: Whether to print progress messages.

    Yields:
        Tuples of (filename, filepath) for each matching file.
    """
    if not os.path.isdir(input_dir):
        log(f"Error: Directory not found: {input_dir}", verbose=True)
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(extension)]
    file_count = len(files)
    log(f"Found {file_count} {extension} file(s) in {input_dir}", verbose)

    for i, filename in enumerate(sorted(files), 1):
        filepath = os.path.join(input_dir, filename)
        log(f"[{i}/{file_count}] Processing: {filename}", verbose)
        yield filename, filepath


def get_output_path(
    input_filename: str,
    output_dir: str,
    suffix: str = "",
    extension: str = ".md"
) -> str:
    """
    Generate a consistent output path for a processed file.

    Args:
        input_filename: The original input filename.
        output_dir: The output directory.
        suffix: Optional suffix to add before the extension (e.g., "_summary").
        extension: The output file extension (default: .md).

    Returns:
        The full output path.
    """
    # Remove existing extension(s) like .pdf.md or .md
    base = input_filename
    for ext in ['.pdf.md', '.md', '.pdf.txt', '.txt']:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break

    output_filename = f"{base}{suffix}{extension}"
    return os.path.join(output_dir, output_filename)


def setup_argparser(
    description: str,
    default_input_dir: str = "plain_texts",
    default_output_dir: str = "outputs"
) -> argparse.ArgumentParser:
    """
    Create an argument parser with common options for document processing scripts.

    Args:
        description: The script description for help text.
        default_input_dir: Default input directory.
        default_output_dir: Default output directory.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--input-dir', '-i',
        default=default_input_dir,
        help=f'Input directory containing documents (default: {default_input_dir})'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default=default_output_dir,
        help=f'Output directory for results (default: {default_output_dir})'
    )
    parser.add_argument(
        '--file', '-f',
        default=None,
        help='Process a single file instead of the entire directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose progress output'
    )
    return parser


def read_document(filepath: str, max_chars: Optional[int] = None, verbose: bool = False) -> Optional[str]:
    """
    Read a document file and return its content.

    Args:
        filepath: Path to the document file.
        max_chars: Maximum number of characters to read (default: None = no limit).
                   Set to None to read full document for proper chunking.
        verbose: Whether to print progress messages.

    Returns:
        The document content, or None if an error occurred.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if max_chars and len(content) > max_chars:
                log(f"Truncating content to {max_chars} characters", verbose)
                content = content[:max_chars]
            return content
    except FileNotFoundError:
        log(f"Error: File not found: {filepath}", verbose=True)
        return None
    except Exception as e:
        log(f"Error reading file {filepath}: {e}", verbose=True)
        return None


def save_output(filepath: str, content: str, verbose: bool = False) -> bool:
    """
    Save content to a file, creating directories as needed.

    Args:
        filepath: Path to the output file.
        content: Content to write.
        verbose: Whether to print progress messages.

    Returns:
        True if successful, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"Saved: {filepath}", verbose)
        return True
    except Exception as e:
        log(f"Error saving file {filepath}: {e}", verbose=True)
        return False


# ============================================================================
# Groq API Client
# ============================================================================

_groq_client = None

def get_groq_client() -> Optional["Groq"]:
    """
    Get or create a Groq API client.
    
    Returns:
        Groq client instance, or None if not available.
    """
    global _groq_client
    
    if Groq is None:
        log("Error: groq package not installed. Run: pip install groq", verbose=True)
        return None
    
    if _groq_client is None:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            log("Error: GROQ_API_KEY not set. Copy .env.example to .env and add your key.", verbose=True)
            return None
        _groq_client = Groq(api_key=GROQ_API_KEY)
    
    return _groq_client


def ask_groq(
    prompt: str,
    context: str,
    model: str = None,
    system_prompt: str = "You are an expert legal assistant analyzing inquest documents.",
    verbose: bool = False
) -> Optional[str]:
    """
    Query the Groq API (Llama 3.3 70B) with a given prompt and context.
    
    Includes automatic rate limiting and retry logic for API errors.

    Args:
        prompt: The prompt or question to ask the model.
        context: The context or document text to provide to the model.
        model: The Groq model to use (default: from config).
        system_prompt: The system prompt for the model.
        verbose: Whether to print progress messages.

    Returns:
        The model's response, or None if an error occurred.
    """
    client = get_groq_client()
    if client is None:
        return None
    
    model = model or GROQ_MODEL
    
    for attempt in range(MAX_RETRIES):
        try:
            log(f"Querying Groq {model}...", verbose)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"}
                ],
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=4096
            )
            
            # Rate limit delay after successful call
            time.sleep(RATE_LIMIT_DELAY)
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Show full error details for debugging
            import traceback
            log(f"Error querying Groq (attempt {attempt + 1}/{MAX_RETRIES}): {type(e).__name__}: {e}", verbose=True)
            if verbose:
                log(traceback.format_exc(), verbose=True)
            
            error_str = str(e).lower()
            
            # Handle rate limiting
            if "rate" in error_str or "429" in error_str or "rate_limit" in error_str:
                wait_time = BACKOFF_BASE ** (attempt + 1)
                log(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{MAX_RETRIES}...", verbose=True)
                time.sleep(wait_time)
                continue
            
            # For other errors, retry with backoff
            if attempt < MAX_RETRIES - 1:
                wait_time = BACKOFF_BASE ** attempt
                log(f"Retrying in {wait_time}s...", verbose)
                time.sleep(wait_time)
            else:
                return None
    
    return None


# ============================================================================
# Citation Validation
# ============================================================================

# Regex pattern to extract citations like [Page 3, Lines 12-15] or [Page 3, Line 12]
CITATION_PATTERN = re.compile(
    r'\[(?:Page\s*)?(\d+),?\s*Lines?\s*(\d+)(?:\s*-\s*(\d+))?\]',
    re.IGNORECASE
)

# Also match file-specific citations like [dec_01.pdf.md, Page 3, Lines 12-15]
FULL_CITATION_PATTERN = re.compile(
    r'\[([^,\]]+),?\s*Page\s*(\d+),?\s*Lines?\s*(\d+)(?:\s*-\s*(\d+))?\]',
    re.IGNORECASE
)


def extract_citations(text: str) -> list[dict]:
    """
    Extract all citations from response text.
    
    Args:
        text: The LLM response text.
        
    Returns:
        List of citation dicts with keys: file_name, page, line_start, line_end, raw
    """
    citations = []
    
    # Find full citations with file names
    for match in FULL_CITATION_PATTERN.finditer(text):
        citations.append({
            "file_name": match.group(1).strip(),
            "page": int(match.group(2)),
            "line_start": int(match.group(3)),
            "line_end": int(match.group(4)) if match.group(4) else int(match.group(3)),
            "raw": match.group(0)
        })
    
    # Find simple citations without file names
    for match in CITATION_PATTERN.finditer(text):
        # Skip if this is part of a full citation we already found
        raw = match.group(0)
        if any(raw in c["raw"] for c in citations):
            continue
            
        citations.append({
            "file_name": None,
            "page": int(match.group(1)),
            "line_start": int(match.group(2)),
            "line_end": int(match.group(3)) if match.group(3) else int(match.group(2)),
            "raw": raw
        })
    
    return citations


def validate_citations(
    response_text: str, 
    source_nodes: list,
    verbose: bool = True
) -> tuple[list[dict], list[dict]]:
    """
    Validate citations in the response against source nodes.
    
    Args:
        response_text: The LLM response text containing citations.
        source_nodes: List of source nodes with metadata (from query response).
        verbose: Whether to print warnings for missing citations.
        
    Returns:
        Tuple of (valid_citations, missing_citations)
    """
    citations = extract_citations(response_text)
    
    if not citations:
        if verbose and WARN_ON_MISSING_CITATIONS:
            log("⚠️  No citations found in response. Consider requesting citations.", verbose=True)
        return [], []
    
    # Build a lookup of available page/line ranges from source nodes
    available_refs = []
    for node in source_nodes:
        if hasattr(node, 'node'):
            meta = node.node.metadata
        elif hasattr(node, 'metadata'):
            meta = node.metadata
        else:
            continue
            
        available_refs.append({
            "file_name": meta.get("file_name"),
            "page": meta.get("page_number"),
            "line_start": meta.get("line_start"),
            "line_end": meta.get("line_end")
        })
    
    valid = []
    missing = []
    
    for citation in citations:
        found = False
        
        for ref in available_refs:
            # Check if citation matches any source
            page_match = citation["page"] == ref["page"]
            
            # Check line overlap
            if ref["line_start"] and ref["line_end"]:
                line_overlap = (
                    citation["line_start"] <= ref["line_end"] and 
                    citation["line_end"] >= ref["line_start"]
                )
            else:
                line_overlap = True  # Can't verify lines, assume OK
            
            # Check file name if provided
            if citation["file_name"] and ref["file_name"]:
                file_match = citation["file_name"].lower() in ref["file_name"].lower()
            else:
                file_match = True  # No file to check
            
            if page_match and line_overlap and file_match:
                found = True
                break
        
        if found:
            valid.append(citation)
        else:
            missing.append(citation)
            if verbose and WARN_ON_MISSING_CITATIONS:
                log(f"⚠️  Citation not found in sources: {citation['raw']}", verbose=True)
    
    if verbose and citations:
        total = len(citations)
        valid_count = len(valid)
        log(f"📚 Citation validation: {valid_count}/{total} citations verified in sources", verbose=True)
    
    return valid, missing


def format_citation_summary(valid: list[dict], missing: list[dict]) -> str:
    """
    Format a summary of citation validation results.
    
    Args:
        valid: List of valid citations.
        missing: List of missing/unverified citations.
        
    Returns:
        Formatted summary string.
    """
    lines = ["\n--- Citation Verification Summary ---"]
    
    total = len(valid) + len(missing)
    if total == 0:
        lines.append("No citations found in response.")
    else:
        lines.append(f"Total citations: {total}")
        lines.append(f"✅ Verified: {len(valid)}")
        lines.append(f"⚠️  Unverified: {len(missing)}")
        
        if missing:
            lines.append("\nUnverified citations:")
            for c in missing:
                lines.append(f"  - {c['raw']}")
    
    lines.append("-" * 40)
    return "\n".join(lines)

