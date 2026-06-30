"""scripts/add_content_volume.py — Inject `Content volume:` line into every YAML template header.

Heuristic for initial value (operator may hand-edit afterwards):
  light    — file < 80 lines AND no columnsgrid mention
  rich     — file > 220 lines OR ≥6 columnsgrid blocks OR ≥4 tabs/accordion items
  standard — everything in between (the common case)

Idempotent: if a `Content volume:` line already exists, skips the file.
Inserts the new line directly after `Visual style:`. If `Visual style:` is
absent, inserts before `Perfect for:` or as the last comment line.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "example_templates"


def classify(content: str) -> str:
    lines = content.splitlines()
    line_count = len(lines)
    columnsgrid_blocks = content.count("name: columnsgrid")
    tab_count = len(re.findall(r"^\s*-\s*name:\s*tabs?\b", content, flags=re.MULTILINE))
    accordion_count = content.count("name: accordion")

    if line_count > 220 or columnsgrid_blocks >= 6 or tab_count + accordion_count >= 4:
        return "rich"
    if line_count < 80 and columnsgrid_blocks == 0:
        return "light"
    return "standard"


def header_block_end(lines: list[str]) -> int:
    """Return index of first non-comment, non-blank line (end of header block)."""
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#"):
            continue
        if s == "":
            continue
        return i
    return len(lines)


def insert_content_volume(text: str, value: str) -> str | None:
    """Return new file text with Content volume line inserted, or None if already present."""
    lines = text.splitlines(keepends=False)
    keep_eol = "\r\n" if text.endswith("\r\n") or "\r\n" in text[:200] else "\n"

    end_idx = header_block_end(lines)
    header = lines[:end_idx]
    rest = lines[end_idx:]

    # Already present? skip.
    for h in header:
        if re.match(r"^\s*#\s*content volume\s*:", h, flags=re.IGNORECASE):
            return None

    new_line = f"# Content volume: {value}"

    # Prefer inserting after Visual style:
    insert_at = None
    for i, h in enumerate(header):
        if re.match(r"^\s*#\s*visual style\s*:", h, flags=re.IGNORECASE):
            insert_at = i + 1
            break
    if insert_at is None:
        # Fall back to before Perfect for:
        for i, h in enumerate(header):
            if re.match(r"^\s*#\s*(perfect for|use cases|best for)\s*:", h, flags=re.IGNORECASE):
                insert_at = i
                break
    if insert_at is None:
        # Last resort — append to header block.
        insert_at = len(header)

    new_header = header[:insert_at] + [new_line] + header[insert_at:]
    return keep_eol.join(new_header + rest) + (keep_eol if text.endswith(("\n", "\r\n")) else "")


def main(dry_run: bool) -> int:
    files = sorted(ROOT.rglob("*.yaml"))
    by_volume = {"light": 0, "standard": 0, "rich": 0}
    skipped = 0
    written = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        volume = classify(text)
        new_text = insert_content_volume(text, volume)
        if new_text is None:
            skipped += 1
            continue
        by_volume[volume] += 1
        if dry_run:
            print(f"DRY  {f.relative_to(ROOT.parent)}  -> {volume}")
        else:
            f.write_text(new_text, encoding="utf-8")
            written += 1
    print()
    print(f"Total YAML files: {len(files)}")
    print(f"Already had Content volume: {skipped}")
    print(f"Would update: {sum(by_volume.values())} (light={by_volume['light']}, standard={by_volume['standard']}, rich={by_volume['rich']})")
    if not dry_run:
        print(f"Wrote {written} files.")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(main(dry))
