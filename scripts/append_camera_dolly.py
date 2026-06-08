from __future__ import annotations

"""
Utility to append " The camera dollies in slowly." to text files safely.

Rules implemented:
- Read only from USER-FILES/04.INPUT/<subdir>
- Write to USER-FILES/05.OUTPUT/YYMMDD_HHMMSS/<subdir>
- Preserve directory structure (non-recursive by default)
- Use pathlib.Path, type hints, small functions, and docstrings
- Idempotent by default: skip if already appended

This script does NOT modify input files.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import sys
from typing import List, Tuple

SENTENCE: str = " The camera dollies in slowly."


def transform_text(
    content: str,
    *,
    sentence: str = SENTENCE,
    idempotent: bool = True,
    require_terminal_period: bool = True,
) -> str:
    """Return content with the sentence inserted after the last terminal period.

    Behavior:
    - If content (ignoring trailing whitespace) already ends with `sentence`, return unchanged when idempotent.
    - If the last non-whitespace character is a period, insert `sentence` immediately after that period and
      before any trailing whitespace/newlines to keep exact one space before the sentence.
    - If no terminal period exists and `require_terminal_period` is True, append ". " + sentence.strip().
    - Otherwise, just append `sentence` at the textual end.

    This aims to produce: "...last sentence. The camera dollies in slowly.\n" while preserving trailing whitespace.
    """
    # Separate trailing whitespace (including newlines) to preserve at the end
    tail_ws_len = len(content) - len(content.rstrip("\t \r\n"))
    trailing = content[-tail_ws_len:] if tail_ws_len else ""
    body = content[:-tail_ws_len] if tail_ws_len else content

    if idempotent and body.endswith(sentence):
        return content  # unchanged

    # Find last period in the textual body
    last_period = body.rfind(".")

    # Case 1: terminal period exists (period is last non-whitespace char)
    if last_period == len(body) - 1 and last_period != -1:
        # Insert exactly after the period, keep one space before the sentence
        new_body = body + sentence
        return new_body + trailing

    # Case 2: no period at the end
    if last_period == -1 or last_period < len(body) - 1:
        if require_terminal_period:
            # Ensure proper sentence separation
            sep = ". " if (len(body) == 0 or not body.endswith(".")) else " "
            new_body = body + sep + sentence.lstrip()
            return new_body + trailing
        else:
            new_body = body + sentence
            return new_body + trailing

    # Fallback (should not be reached due to conditions above)
    return body + sentence + trailing


@dataclass
class RunConfig:
    input_dir: Path
    output_root: Path
    target_subdir: Path
    recursive: bool
    pattern: str
    dry_run: bool
    idempotent: bool
    require_terminal_period: bool


def discover_files(base: Path, pattern: str, recursive: bool) -> List[Path]:
    """Discover files matching pattern under base.

    - Non-recursive uses Path.glob(f"{pattern}")
    - Recursive uses rglob
    """
    if recursive:
        return sorted([p for p in base.rglob(pattern) if p.is_file()])
    return sorted([p for p in base.glob(pattern) if p.is_file()])


def make_timestamp_dir(root: Path) -> Path:
    """Create and return a YYMMDD_HHMMSS directory under root (not created when dry-run)."""
    ts = datetime.now().strftime("%y%m%d_%H%M%S")
    return root / ts


def process_files(cfg: RunConfig) -> Tuple[int, int, List[Tuple[Path, str]]]:
    """Process files and write to timestamped output, returning stats and errors.

    Returns (processed_count, skipped_count, errors)
    where errors is a list of (path, message).
    """
    errors: List[Tuple[Path, str]] = []
    files = discover_files(cfg.input_dir / cfg.target_subdir, cfg.pattern, cfg.recursive)

    ts_dir = make_timestamp_dir(cfg.output_root)
    out_dir = ts_dir / cfg.target_subdir

    processed = 0
    skipped = 0

    for idx, src in enumerate(files, start=1):
        try:
            rel = src.relative_to(cfg.input_dir)
            dest = ts_dir / rel
            if not cfg.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)

            text = src.read_text(encoding="utf-8")
            new_text = transform_text(
                text,
                sentence=SENTENCE,
                idempotent=cfg.idempotent,
                require_terminal_period=cfg.require_terminal_period,
            )

            if new_text == text:
                skipped += 1
            else:
                processed += 1
            if not cfg.dry_run:
                dest.write_text(new_text, encoding="utf-8")

            # Simple progress line
            print(f"[{idx}/{len(files)}] {'DRY-RUN ' if cfg.dry_run else ''}{src}")
        except Exception as e:  # noqa: BLE001
            errors.append((src, str(e)))
            # Continue with next file

    # Report output dir for visibility
    print(f"Output directory: {out_dir.parent if not cfg.dry_run else '(dry-run)'}")
    return processed, skipped, errors


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    p = argparse.ArgumentParser(description="Append camera dolly sentence to text prompts (safe copy)")
    p.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Path to USER-FILES directory containing 04.INPUT",
    )
    p.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Path to USER-FILES/05.OUTPUT (timestamped subdir is created)",
    )
    p.add_argument(
        "--target-subdir",
        type=Path,
        default=Path("04.INPUT/04.3.PROMPT"),
        help="Subdirectory under input-dir to process",
    )
    p.add_argument("--recursive", action="store_true", help="Recurse into subdirectories")
    p.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern to match files (default: *.txt)",
    )
    p.add_argument("--dry-run", action="store_true", help="Do not write files; just simulate")
    p.add_argument(
        "--no-idempotent",
        action="store_true",
        help="Do not skip files already ending with the sentence",
    )
    p.add_argument(
        "--no-require-terminal-period",
        action="store_true",
        help="If set, will not add a period when missing",
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    """Entry point."""
    args = parse_args(argv)
    cfg = RunConfig(
        input_dir=args.input_dir,
        output_root=args.output_root,
        target_subdir=args.target_subdir,
        recursive=args.recursive,
        pattern=args.pattern,
        dry_run=args.dry_run,
        idempotent=not args.no_idempotent,
        require_terminal_period=not args.no_require_terminal_period,
    )
    processed, skipped, errors = process_files(cfg)

    print(f"Processed: {processed}, Skipped: {skipped}, Errors: {len(errors)}")
    if errors:
        for pth, msg in errors:
            print(f"ERROR: {pth}: {msg}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

