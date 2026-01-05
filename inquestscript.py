"""
inquestscript.py

Query documents using Groq (Llama 3.3 70B) or local Ollama to generate summaries.

This script processes markdown documents and generates AI-powered summaries
with citation verification for legal accuracy.

Large documents are automatically chunked to stay within API token limits.

Usage:
    python inquestscript.py                      # Process all documents with Groq
    python inquestscript.py -f document.md       # Process single file
    python inquestscript.py --use-ollama         # Use local Ollama instead
    python inquestscript.py -p "Custom prompt"   # Use custom prompt
"""

import os
import argparse
import time
from utils import (
    ask_llama,
    ask_groq,
    iterate_documents,
    get_output_path,
    read_document,
    save_output,
    log,
    extract_citations,
    format_citation_summary
)

# ============================================================================
# Chunking Configuration for Groq Token Limits
# ============================================================================

# Groq free tier limit is 12,000 tokens per request
# ~4 chars per token, leaving room for prompt (~1000 tokens) and response (~4000 tokens)
# Conservative estimate: 7000 tokens for context = ~28,000 chars
MAX_CHUNK_CHARS = 25000  # ~6,250 tokens for document content

# Overlap between chunks to preserve context at boundaries
CHUNK_OVERLAP_CHARS = 2000  # ~500 tokens overlap

# Import config for citation instructions
try:
    from config import CITATION_INSTRUCTION
except ImportError:
    CITATION_INSTRUCTION = (
        "You MUST cite specific page and line numbers for every factual claim using this format: "
        "[Page X, Lines Y-Z] or [Page X, Line Y]. "
        "If you cannot find a specific reference, state 'Reference not located in provided excerpts.'"
    )


# Base instructions with citation requirement
INSTRUCTIONS = (
    "Instructions: Only answer using information found in the provided document. "
    "If the answer is not present, say 'Not found in the document.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
    f"{CITATION_INSTRUCTION}\n\n"
)

DEFAULT_QUESTION = (
    "Summarize the main findings of this document. "
    "Highlight key evidence, testimony, and any issues or concerns raised. "
    "Cite specific page and line numbers for each finding."
)

# Prompt for summarizing individual chunks
CHUNK_SUMMARY_PROMPT = (
    "Summarize this portion of the document. "
    "Focus on key evidence, testimony, and any issues or concerns raised. "
    "Cite specific page and line numbers for each finding."
)

# Prompt for synthesizing multiple chunk summaries
SYNTHESIS_PROMPT = (
    "Below are summaries from different sections of the same document. "
    "Synthesize these into a single coherent summary that:\n"
    "1. Highlights the main findings across all sections\n"
    "2. Identifies key evidence and testimony\n"
    "3. Notes any issues or concerns raised\n"
    "4. Preserves all page and line citations from the section summaries\n\n"
    "Do not add any information not present in these summaries."
)


def chunk_document(text: str, max_chars: int = MAX_CHUNK_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[tuple[str, int]]:
    """
    Split a document into overlapping chunks that fit within token limits.
    
    Attempts to split at paragraph boundaries (double newlines) for cleaner breaks.
    
    Args:
        text: The full document text.
        max_chars: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.
        
    Returns:
        List of (chunk_text, chunk_number) tuples.
    """
    if len(text) <= max_chars:
        return [(text, 1)]
    
    chunks = []
    start = 0
    chunk_num = 1
    
    while start < len(text):
        # Calculate end position
        end = start + max_chars
        
        if end >= len(text):
            # Last chunk
            chunks.append((text[start:], chunk_num))
            break
        
        # Try to find a good break point (paragraph boundary)
        # Look backwards from end for a double newline
        break_point = text.rfind('\n\n', start + max_chars // 2, end)
        
        if break_point == -1:
            # No paragraph break found, try single newline
            break_point = text.rfind('\n', start + max_chars // 2, end)
        
        if break_point == -1:
            # No newline found, just cut at max_chars
            break_point = end
        else:
            # Include the newline in the chunk
            break_point += 1
        
        chunks.append((text[start:break_point], chunk_num))
        chunk_num += 1
        
        # Move start back by overlap amount for context continuity
        start = break_point - overlap
        if start < 0:
            start = break_point
    
    return chunks


def setup_argparser() -> argparse.ArgumentParser:
    """Create argument parser with options for document processing."""
    parser = argparse.ArgumentParser(
        description="Generate AI summaries of documents using Groq (Llama 3.3 70B)"
    )
    parser.add_argument(
        '--input-dir', '-i',
        default="plain_texts",
        help='Input directory containing documents (default: plain_texts)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default="summaries",
        help='Output directory for results (default: summaries)'
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
    parser.add_argument(
        '--use-ollama',
        action='store_true',
        help='Use local Ollama instead of Groq API (slower but free)'
    )
    parser.add_argument(
        '--prompt', '-p',
        default=None,
        help='Custom prompt to use instead of default summary prompt'
    )
    return parser


def process_document(
    filepath: str, 
    output_dir: str, 
    prompt: str = None,
    use_ollama: bool = False,
    verbose: bool = False
) -> bool:
    """
    Process a single document and generate a summary.
    
    Large documents are automatically split into chunks, processed separately,
    and then synthesized into a final summary.

    Args:
        filepath: Path to the input document.
        output_dir: Directory to save the summary.
        prompt: Custom prompt (uses default if None).
        use_ollama: Use local Ollama instead of Groq.
        verbose: Whether to print progress messages.

    Returns:
        True if successful, False otherwise.
    """
    # Read full document (no truncation)
    context = read_document(filepath, max_chars=None, verbose=verbose)
    if not context:
        return False

    # Use custom prompt or default
    question = prompt or DEFAULT_QUESTION
    
    # Check if document needs chunking (only for Groq, Ollama can handle larger contexts)
    if not use_ollama and len(context) > MAX_CHUNK_CHARS:
        log(f"Document is {len(context):,} chars, splitting into chunks...", verbose=True)
        answer = process_chunked_document(context, question, verbose)
    else:
        # Process as single document
        full_prompt = INSTRUCTIONS + question
        
        if use_ollama:
            answer = ask_llama(full_prompt, context, verbose=verbose)
        else:
            answer = ask_groq(
                full_prompt, 
                context, 
                system_prompt="You are an expert legal assistant analyzing inquest documents.",
                verbose=verbose
            )

    if not answer:
        log(f"Failed to get response for {filepath}", verbose=True)
        return False

    # Validate citations in response
    citations = extract_citations(answer)
    citation_summary = format_citation_summary(citations, [])
    
    # Format output
    filename = os.path.basename(filepath)
    output_path = get_output_path(filename, output_dir, suffix="_summary", extension=".txt")
    
    content = (
        f"SOURCE: {filename}\n"
        f"PROMPT: {question}\n\n"
        f"RESPONSE:\n{answer}\n"
        f"{citation_summary}"
    )
    
    return save_output(output_path, content, verbose)


def process_chunked_document(context: str, question: str, verbose: bool = False) -> str:
    """
    Process a large document by splitting into chunks, summarizing each,
    then synthesizing the chunk summaries into a final response.
    
    Args:
        context: The full document text.
        question: The user's question/prompt.
        verbose: Whether to print progress messages.
        
    Returns:
        The synthesized summary, or None if processing failed.
    """
    chunks = chunk_document(context)
    log(f"Split document into {len(chunks)} chunks", verbose=True)
    
    chunk_summaries = []
    
    for chunk_text, chunk_num in chunks:
        log(f"Processing chunk {chunk_num}/{len(chunks)} ({len(chunk_text):,} chars)...", verbose=True)
        
        # For individual chunks, use the chunk summary prompt
        chunk_prompt = INSTRUCTIONS + CHUNK_SUMMARY_PROMPT
        
        chunk_answer = ask_groq(
            chunk_prompt,
            chunk_text,
            system_prompt="You are an expert legal assistant analyzing inquest documents.",
            verbose=verbose
        )
        
        if chunk_answer:
            chunk_summaries.append(f"=== Section {chunk_num} ===\n{chunk_answer}")
        else:
            log(f"Warning: Failed to process chunk {chunk_num}", verbose=True)
        
        # Small delay between chunks to avoid rate limiting
        time.sleep(1)
    
    if not chunk_summaries:
        return None
    
    # If only one chunk succeeded, return it directly
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    # Synthesize all chunk summaries into final response
    log(f"Synthesizing {len(chunk_summaries)} chunk summaries...", verbose=True)
    
    combined_summaries = "\n\n".join(chunk_summaries)
    
    # Check if combined summaries are too large for synthesis
    if len(combined_summaries) > MAX_CHUNK_CHARS:
        # Summaries are still too large, do hierarchical synthesis
        log("Chunk summaries too large, performing hierarchical synthesis...", verbose=True)
        return hierarchical_synthesis(chunk_summaries, verbose)
    
    synthesis_prompt = SYNTHESIS_PROMPT + f"\n\nOriginal question: {question}"
    
    final_answer = ask_groq(
        synthesis_prompt,
        combined_summaries,
        system_prompt="You are an expert legal assistant synthesizing document summaries.",
        verbose=verbose
    )
    
    return final_answer


def hierarchical_synthesis(summaries: list[str], verbose: bool = False) -> str:
    """
    Recursively synthesize summaries when they're too large for a single pass.
    
    Args:
        summaries: List of chunk summaries.
        verbose: Whether to print progress messages.
        
    Returns:
        The final synthesized summary.
    """
    # Group summaries into batches that fit within token limits
    batch_size = 3  # Process 3 summaries at a time
    intermediate_summaries = []
    
    for i in range(0, len(summaries), batch_size):
        batch = summaries[i:i + batch_size]
        combined = "\n\n".join(batch)
        
        log(f"Synthesizing batch {i // batch_size + 1}...", verbose=True)
        
        batch_summary = ask_groq(
            SYNTHESIS_PROMPT,
            combined,
            system_prompt="You are an expert legal assistant synthesizing document summaries.",
            verbose=verbose
        )
        
        if batch_summary:
            intermediate_summaries.append(batch_summary)
        
        time.sleep(1)
    
    # If we've reduced to few enough summaries, do final synthesis
    if len(intermediate_summaries) <= 3:
        combined = "\n\n".join(intermediate_summaries)
        return ask_groq(
            SYNTHESIS_PROMPT,
            combined,
            system_prompt="You are an expert legal assistant synthesizing document summaries.",
            verbose=verbose
        )
    
    # Otherwise, recurse
    return hierarchical_synthesis(intermediate_summaries, verbose)


def main():
    parser = setup_argparser()
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Print mode info
    mode = "Ollama (local)" if args.use_ollama else "Groq API (Llama 3.3 70B)"
    print(f"\n🔧 Mode: {mode}")
    if args.prompt:
        print(f"📝 Custom prompt: {args.prompt[:50]}...")
    print()

    if args.file:
        # Process single file
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}")
            return 1

        log(f"Processing single file: {args.file}", args.verbose)
        success = process_document(
            args.file, args.output_dir,
            prompt=args.prompt,
            use_ollama=args.use_ollama,
            verbose=args.verbose
        )
        status = "✅ Success" if success else "❌ Failed"
        print(f"\n{status}")
        return 0 if success else 1

    # Process all documents in directory
    success_count = 0
    error_count = 0

    for filename, filepath in iterate_documents(args.input_dir, extension=".md", verbose=args.verbose):
        print(f"📄 Processing: {filename}")
        success = process_document(
            filepath, args.output_dir,
            prompt=args.prompt,
            use_ollama=args.use_ollama,
            verbose=args.verbose
        )
        if success:
            success_count += 1
        else:
            error_count += 1

    print(f"\n{'='*50}")
    print(f"✅ Completed: {success_count} documents processed")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Results saved to: {args.output_dir}")
    print(f"{'='*50}")
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())
