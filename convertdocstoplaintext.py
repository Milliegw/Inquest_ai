"""
Convert PDF documents to Markdown format.

This script extracts text from PDF files and saves them as Markdown and TXT files
with a title heading based on the filename.
"""

import os
import argparse
from pathlib import Path
import pdfplumber

# Security: Maximum file size to process (100MB)
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024


def convert_pdf_to_markdown(
    pdf_path: str, 
    output_path: str, 
    base_dir: str | None = None,
    verbose: bool = False
) -> bool:
    """
    Convert a single PDF file to Markdown and TXT format.

    Args:
        pdf_path: Path to the input PDF file.
        output_path: Path for the output Markdown file.
        base_dir: Base directory for path validation (security).
        verbose: Whether to print progress messages.

    Returns:
        True if successful, False otherwise.
    """
    # Security: Validate paths to prevent directory traversal attacks
    pdf_resolved = Path(pdf_path).resolve()
    output_resolved = Path(output_path).resolve()
    
    if base_dir:
        base_resolved = Path(base_dir).resolve()
        if not pdf_resolved.is_relative_to(base_resolved):
            print(f"Security Error: Input path escapes base directory: {pdf_path}")
            return False
        if not output_resolved.is_relative_to(base_resolved):
            print(f"Security Error: Output path escapes base directory: {output_path}")
            return False
    
    # Security: Check file size before processing
    try:
        file_size = pdf_resolved.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            print(f"Security Error: File too large ({file_size} bytes): {pdf_path}")
            return False
    except OSError as e:
        print(f"Error accessing file {pdf_path}: {e}")
        return False
    
    # Security: Ensure we're not following symlinks to unexpected locations
    if pdf_resolved.is_symlink():
        print(f"Security Warning: Skipping symlink: {pdf_path}")
        return False

    if verbose:
        print(f"Processing: {pdf_path}")

    try:
        with pdfplumber.open(str(pdf_resolved)) as pdf:
            pages = []
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages.append(page_text)
                if verbose:
                    print(f"  Extracted page {i}/{len(pdf.pages)}")

            text = "\n\n".join(pages)

        # Create markdown content with title heading
        filename = os.path.basename(pdf_path)
        title = filename.replace(".pdf", "").replace("_", " ").replace("-", " ")
        markdown_content = f"# {title}\n\n{text}"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Write Markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        if verbose:
            print(f"Saved: {output_path}")

        # Write plain text file (without Markdown heading)
        txt_path = output_path.replace('.md', '.txt')
        if not os.path.exists(txt_path):
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            if verbose:
                print(f"Saved: {txt_path}")

        return True

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to Markdown format"
    )
    parser.add_argument(
        '--input-dir', '-i',
        default='downloads',
        help='Input directory containing PDF files (default: downloads)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='Output directory for Markdown files (default: same as input)'
    )
    parser.add_argument(
        '--file', '-f',
        default=None,
        help='Process a single PDF file instead of the entire directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose progress output'
    )
    args = parser.parse_args()

    output_dir = args.output_dir or args.input_dir
    
    # Security: Establish base directory for path validation
    base_dir = Path(os.getcwd()).resolve()

    if args.file:
        # Process single file
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}")
            return 1

        filename = os.path.basename(args.file)
        md_path = os.path.join(output_dir, filename + ".md")
        success = convert_pdf_to_markdown(args.file, md_path, str(base_dir), args.verbose)
        return 0 if success else 1

    # Process all PDFs in directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory not found: {args.input_dir}")
        return 1

    pdf_files = [f for f in os.listdir(args.input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in {args.input_dir}")
        return 0

    if args.verbose:
        print(f"Found {len(pdf_files)} PDF file(s) in {args.input_dir}")

    success_count = 0
    error_count = 0

    for i, filename in enumerate(sorted(pdf_files), 1):
        if args.verbose:
            print(f"\n[{i}/{len(pdf_files)}] {filename}")

        pdf_path = os.path.join(args.input_dir, filename)
        md_path = os.path.join(output_dir, filename + ".md")

        if convert_pdf_to_markdown(pdf_path, md_path, str(base_dir), args.verbose):
            success_count += 1
        else:
            error_count += 1

    print(f"\nCompleted: {success_count} converted, {error_count} errors")
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())