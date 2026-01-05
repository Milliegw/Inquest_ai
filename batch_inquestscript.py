"""
batch_inquestscript.py

Batch process documents with multiple scenario prompts using Groq (Llama 3.3 70B).

This script processes all markdown documents in a directory and runs
multiple role-based scenario prompts on each document, with citation
verification for legal accuracy.

Usage:
    python batch_inquestscript.py                    # Process all documents
    python batch_inquestscript.py -f doc.md          # Process single file
    python batch_inquestscript.py --use-ollama       # Use local Ollama instead of Groq
    python batch_inquestscript.py -v                 # Verbose output
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
    format_citation_summary,
    RATE_LIMIT_DELAY
)

# Import config for citation instructions
try:
    from config import CITATION_INSTRUCTION
except ImportError:
    CITATION_INSTRUCTION = (
        "You MUST cite specific page and line numbers for every factual claim using this format: "
        "[Page X, Lines Y-Z] or [Page X, Line Y]. "
        "If you cannot find a specific reference, state 'Reference not located in provided excerpts.'"
    )


# Scenario prompts for different perspectives (updated with citation requirements)
PROMPTS = [
    (
        "family",
        "If you were representing the family, what evidence would you focus on to challenge the police narrative? "
        "Provide a detailed analysis of each piece of evidence, identifying potential inconsistencies or contradictions. "
        "For each point, cite specific page and line numbers from the document. "
        "Structure your response with clear headings for each evidence point and conclude with actionable next steps."
    ),
    (
        "coroner",
        "Summarize the main findings relevant to the coroner's decision-making. "
        "Include detailed explanations of key evidence with specific page and line citations. "
        "Organize the response with structured sections for clarity. "
        "Highlight any ambiguities or gaps in evidence that could impact decision-making."
    ),
    (
        "police",
        "What evidence supports the police's version of events? "
        "Provide an in-depth analysis of each supporting piece of evidence, citing specific page and line numbers. "
        "Format the response with clear headings for each evidence item. "
        "Address potential counterarguments and conclude with recommendations for addressing weaknesses."
    ),
]

# Base instructions with citation requirement
INSTRUCTIONS = (
    "Instructions: Only answer using information found in the provided document. "
    "If the answer is not present, say 'Not found in the document.' "
    "Do not speculate, invent facts, or use outside knowledge. "
    "Be concise and objective.\n\n"
    f"{CITATION_INSTRUCTION}\n\n"
)


def setup_argparser() -> argparse.ArgumentParser:
    """Create argument parser with options for batch processing."""
    parser = argparse.ArgumentParser(
        description="Batch process documents with scenario prompts using Groq (Llama 3.3 70B)"
    )
    parser.add_argument(
        '--input-dir', '-i',
        default="plain_texts",
        help='Input directory containing documents (default: plain_texts)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default="scenario_outputs_new",
        help='Output directory for results (default: scenario_outputs_new)'
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
        '--scenario', '-s',
        choices=['family', 'coroner', 'police'],
        default=None,
        help='Run only a specific scenario (default: all)'
    )
    return parser


def process_document(
    filepath: str, 
    output_dir: str, 
    use_ollama: bool = False,
    scenario_filter: str = None,
    verbose: bool = False
) -> tuple[int, int]:
    """
    Process a single document with scenario prompts.

    Args:
        filepath: Path to the input document.
        output_dir: Directory to save the outputs.
        use_ollama: Use local Ollama instead of Groq.
        scenario_filter: Only run this specific scenario.
        verbose: Whether to print progress messages.

    Returns:
        Tuple of (success_count, error_count) for the prompts.
    """
    # Read full document (no truncation for better context)
    context = read_document(filepath, max_chars=None, verbose=verbose)
    if not context:
        return 0, len(PROMPTS)

    filename = os.path.basename(filepath)
    success_count = 0
    error_count = 0

    # Filter prompts if specific scenario requested
    prompts_to_run = PROMPTS
    if scenario_filter:
        prompts_to_run = [(r, p) for r, p in PROMPTS if r == scenario_filter]

    for role, prompt in prompts_to_run:
        log(f"  Running scenario: {role}", verbose)
        full_prompt = INSTRUCTIONS + prompt
        
        # Use Groq or Ollama based on flag
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
            log(f"  Failed to get response for {role} scenario", verbose=True)
            error_count += 1
            continue

        # Validate citations in response
        citations = extract_citations(answer)
        citation_summary = format_citation_summary(citations, [])  # Can't validate without source nodes
        
        # Format output
        output_path = get_output_path(filename, output_dir, suffix=f"_{role}_scenario", extension=".txt")
        content = (
            f"PROMPT: {prompt}\n\n"
            f"RESPONSE:\n{answer}\n"
            f"{citation_summary}"
        )

        if save_output(output_path, content, verbose):
            success_count += 1
            log(f"  ✅ Saved: {output_path}", verbose)
        else:
            error_count += 1

    return success_count, error_count


def main():
    parser = setup_argparser()
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Print mode info
    mode = "Ollama (local)" if args.use_ollama else "Groq API (Llama 3.3 70B)"
    print(f"\n🔧 Mode: {mode}")
    if args.scenario:
        print(f"📋 Scenario: {args.scenario} only")
    print()

    if args.file:
        # Process single file
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}")
            return 1

        log(f"Processing single file: {args.file}", args.verbose)
        success, errors = process_document(
            args.file, args.output_dir, 
            use_ollama=args.use_ollama,
            scenario_filter=args.scenario,
            verbose=args.verbose
        )
        log(f"\n✅ Completed: {success} scenarios processed, {errors} errors", True)
        return 0 if errors == 0 else 1

    # Process all documents in directory
    total_success = 0
    total_errors = 0
    doc_count = 0

    for filename, filepath in iterate_documents(args.input_dir, extension=".md", verbose=args.verbose):
        doc_count += 1
        print(f"\n📄 [{doc_count}] Processing: {filename}")
        
        success, errors = process_document(
            filepath, args.output_dir,
            use_ollama=args.use_ollama,
            scenario_filter=args.scenario,
            verbose=args.verbose
        )
        total_success += success
        total_errors += errors

    print(f"\n{'='*50}")
    print(f"✅ Completed: {doc_count} documents")
    print(f"   {total_success} scenarios processed")
    print(f"   {total_errors} errors")
    print(f"📁 Results saved to: {args.output_dir}")
    print(f"{'='*50}")
    
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    exit(main())
