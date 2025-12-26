"""
Command-line interface for Snapchat Media Restorer.

This CLI processes exported Snapchat data by reconstructing images and videos
from their original media and overlay files.
"""

import argparse
import sys
from pathlib import Path

from .core import process_data


# ___________________________________________________________________
# Helpers


def confirm_overwrite(path: Path, overwrite: bool) -> bool:
    """
    Decide whether an output path may be written.

    If overwrite is False and any file with the same stem already exists
    (regardless of extension), the operation is skipped.
    """
    if overwrite:
        return True

    if not path.parent.exists():
        return True

    existing = list(path.parent.glob(f"{path.stem}.*"))
    return len(existing) == 0


# ___________________________________________________________________
# CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snap-restore",
        description="Restore Snapchat images and videos by merging media with overlays.",
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input directory containing Snapchat export data",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Output directory for reconstructed media",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files (any extension)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without writing files",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_dir: Path = args.input
    output_dir: Path = args.output

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: input directory does not exist: {input_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Input directory : {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Overwrite        : {args.overwrite}")
        print(f"Dry run          : {args.dry_run}")
        print()

    try:
        if args.dry_run:
            print("Dry run mode enabled — no files will be written.")
            process_data(
                input_dir=input_dir,
                output_dir=output_dir,
            )
            return 0

        process_data(
            input_dir=input_dir,
            output_dir=output_dir,
        )

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.verbose:
        print("Processing completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
