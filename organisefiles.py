"""
Organize converted document files by moving them to the plain_texts directory.

This script moves markdown files (converted from PDFs) from the downloads
directory to the plain_texts directory for further processing.
"""

import os
import shutil
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Move converted markdown files to plain_texts directory"
    )
    parser.add_argument(
        '--src', '-s',
        default='downloads',
        help='Source directory containing converted files (default: downloads)'
    )
    parser.add_argument(
        '--dst', '-d',
        default='plain_texts',
        help='Destination directory (default: plain_texts)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose progress output'
    )
    args = parser.parse_args()

    os.makedirs(args.dst, exist_ok=True)

    files_moved = 0
    errors = 0

    if not os.path.isdir(args.src):
        print(f"Error: Source directory not found: {args.src}")
        return 1

    for f in os.listdir(args.src):
        if f.endswith(".pdf.md"):
            src_path = os.path.join(args.src, f)
            dst_path = os.path.join(args.dst, f)
            try:
                shutil.move(src_path, dst_path)
                files_moved += 1
                if args.verbose:
                    print(f"Moved: {f}")
            except Exception as e:
                print(f"Error moving {f}: {e}")
                errors += 1

    if args.verbose or files_moved > 0 or errors > 0:
        print(f"\nCompleted: {files_moved} files moved, {errors} errors")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit(main())