"""
Query documents using Groq API (Llama 3.3 70B) for analysis.

This script processes markdown documents and queries them using Groq's Llama model.
Note: Requires a valid Groq API key set via GROQ_API_KEY environment variable.

Security: API keys must be provided via environment variables, not CLI arguments.
"""

import os
from utils import (
    ask_groq,
    iterate_documents,
    get_output_path,
    setup_argparser,
    read_document,
    save_output,
    log
)

# Import config for Groq settings
try:
    from config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Maximum context size for Groq queries
GROQ_MAX_CONTEXT = 8000  # Llama 3.3 supports larger context


QUESTION = "Summarize the main findings of this document."


def process_document(filepath: str, output_dir: str, verbose: bool = False) -> bool:
    """
    Process a single document and generate a summary.

    Args:
        filepath: Path to the input document.
        output_dir: Directory to save the summary.
        verbose: Whether to print progress messages.

    Returns:
        True if successful, False otherwise.
    """
    context = read_document(filepath, max_chars=GROQ_MAX_CONTEXT, verbose=verbose)
    if not context:
        return False

    answer = ask_groq(QUESTION, context, verbose=verbose)
    if not answer:
        log(f"Failed to get response for {filepath}", verbose=True)
        return False

    filename = os.path.basename(filepath)
    output_path = get_output_path(filename, output_dir, suffix="_groq_summary", extension=".md")
    return save_output(output_path, answer, verbose)


def main():
    parser = setup_argparser(
        description="Query documents using Groq (Llama 3.3 70B)",
        default_input_dir="plain_texts",
        default_output_dir="groq_outputs"
    )
    args = parser.parse_args()

    if not GROQ_API_KEY:
        print("Error: Groq API key is required. Set GROQ_API_KEY environment variable.")
        print("  Example: export GROQ_API_KEY='your-key-here'")
        print("  Or add GROQ_API_KEY=your-key-here to your .env file")
        return 1

    os.makedirs(args.output_dir, exist_ok=True)

    if args.file:
        # Process single file
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}")
            return 1

        log(f"Processing single file: {args.file}", args.verbose)
        success = process_document(args.file, args.output_dir, args.verbose)
        return 0 if success else 1

    # Process all documents in directory
    success_count = 0
    error_count = 0

    for filename, filepath in iterate_documents(args.input_dir, extension=".md", verbose=args.verbose):
        if process_document(filepath, args.output_dir, args.verbose):
            success_count += 1
        else:
            error_count += 1

    log(f"\nCompleted: {success_count} processed, {error_count} errors", args.verbose)
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())