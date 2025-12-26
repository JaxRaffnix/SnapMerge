from pathlib import Path

import typer

from .core import process_data

app = typer.Typer(
    help="Restore Snapchat images and videos by merging media with overlays."
)


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


@app.command()
def main(
    input: Path = typer.Argument(..., help="Input directory containing Snapchat export data"),
    output: Path = typer.Argument(..., help="Output directory for reconstructed media"),
    overwrite: bool = typer.Option(False, help="Overwrite existing output files (any extension)"),
    dry_run: bool = typer.Option(False, help="Show what would be processed without writing files"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> int:
    if not input.exists() or not input.is_dir():
        typer.echo(f"Error: input directory does not exist: {input}", err=True)
        raise typer.Exit(code=1)

    output.mkdir(parents=True, exist_ok=True)

    if verbose:
        typer.echo(f"Input directory : {input}")
        typer.echo(f"Output directory: {output}")
        typer.echo(f"Overwrite        : {overwrite}")
        typer.echo(f"Dry run          : {dry_run}")
        typer.echo()

    try:
        if dry_run:
            typer.echo("Dry run mode enabled — no files will be written.")

        process_data(input_dir=input, output_dir=output)

    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2)

    if verbose:
        typer.echo("Processing completed successfully.")

    return 0


if __name__ == "__main__":
    app()
