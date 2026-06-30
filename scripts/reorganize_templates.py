"""scripts/reorganize_templates.py — One-shot Phase 2 reorganization.

Moves/renames example_templates/ folders so folder name == canonical section_type.
Run with --dry-run first to preview, then without flag to execute.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "example_templates"

# Style filename prefix → canonical CANONICAL_STYLES key (only where they differ).
STYLE_RENAME = {
    "modern_": "modern_minimalist_",
    "retro_": "retro_vintage_",
    "monochrome_": "monochrome_dark_",
    "y2k_retro_futurism_": "y2k_retro-futurism_",  # note hyphen
}

# Folder rename map (Phase 2C).
FOLDER_RENAMES = {
    "cta_banners": "cta",
    "features_benefits": "features",
    "pricing_plan_cards": "pricing",
    "review_testimonial_cards": "testimonials",
    "portfolio_showcase_cards": "gallery",
    "story_blog_cards": "blog",
    "product_cards": "products",
    "dashboard_data_cards": "dashboard",
    "contact_section": "contact",
    "faq_section": "faq",
    "banner_announcement": "banner",
}


def read_section_type(yaml_path: Path) -> str:
    """Return the value of '# Section type: …' or '' if missing."""
    for line in yaml_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#"):
            t = s.lstrip("#").strip().lower()
            if t.startswith("section type:"):
                return t[len("section type:"):].strip().rstrip(".").lower()
        elif s and not s.startswith("#"):
            break
    return ""


def rename_style_filename(name: str) -> str:
    """Apply STYLE_RENAME prefixes (modern_ → modern_minimalist_, etc.)."""
    for old, new in STYLE_RENAME.items():
        if name.startswith(old):
            return new + name[len(old):]
    return name


def plan_moves() -> list[tuple[Path, Path, str]]:
    """Build the (src, dst, action) move list for the entire Phase 2.

    Action is 'mv' for normal moves or 'rm' when the destination already
    exists with identical bytes (a stale duplicate from a prior botched
    migration). Collisions where bytes differ get a `_v2.yaml` suffix.
    """
    moves: list[tuple[Path, Path, str]] = []
    seen_dsts: set[Path] = set()

    def queue(src: Path, dst: Path) -> None:
        if src == dst:
            return
        # If dst already exists or queued, decide between dedup-delete and rename.
        if dst in seen_dsts or dst.exists():
            if dst.exists() and dst.read_bytes() == src.read_bytes():
                moves.append((src, dst, "rm"))
                return
            # Bytes differ — keep both, suffix the incoming file.
            new_dst = dst.with_name(dst.stem + "_v2" + dst.suffix)
            n = 2
            while new_dst in seen_dsts or new_dst.exists():
                n += 1
                new_dst = dst.with_name(f"{dst.stem}_v{n}{dst.suffix}")
            moves.append((src, new_dst, "mv"))
            seen_dsts.add(new_dst)
            return
        moves.append((src, dst, "mv"))
        seen_dsts.add(dst)

    # Phase 2A — disband styles/
    styles_dir = ROOT / "styles"
    if styles_dir.is_dir():
        for f in sorted(styles_dir.glob("*.yaml")):
            section = read_section_type(f)
            if not section:
                print(f"!! styles/{f.name} has no Section type header — skipped", file=sys.stderr)
                continue
            # Canonicalize section: 'features' ok, 'cta' ok, 'pricing' ok,
            # 'testimonials' ok, 'footer' ok, 'hero' ok.
            target_folder = section
            new_name = rename_style_filename(f.name)
            queue(f, ROOT / target_folder / new_name)

    # Phase 2B — split navigation_footer/
    nf = ROOT / "navigation_footer"
    if nf.is_dir():
        for f in sorted(nf.glob("*.yaml")):
            section = read_section_type(f) or "navigation"
            if section not in {"navigation", "footer"}:
                section = "navigation"
            queue(f, ROOT / section / f.name)

    # Fold titlebar/ → navigation/
    titlebar = ROOT / "titlebar"
    if titlebar.is_dir():
        for f in sorted(titlebar.glob("*.yaml")):
            queue(f, ROOT / "navigation" / f.name)

    # Phase 2C — folder renames (whole-folder, only if target doesn't exist)
    for old, new in FOLDER_RENAMES.items():
        old_dir = ROOT / old
        if old_dir.is_dir():
            for f in sorted(old_dir.glob("*.yaml")):
                queue(f, ROOT / new / f.name)

    # Phase 2C — split team_about/ by header
    ta = ROOT / "team_about"
    if ta.is_dir():
        for f in sorted(ta.glob("*.yaml")):
            section = read_section_type(f)
            target = section if section in {"team", "about"} else "about"
            queue(f, ROOT / target / f.name)

    # Phase 2C — split counter-up/ by header
    cu = ROOT / "counter-up"
    if cu.is_dir():
        for f in sorted(cu.glob("*.yaml")):
            section = read_section_type(f)
            target = section if section in {"stats", "achievements"} else "stats"
            queue(f, ROOT / target / f.name)

    # Phase 2C — merge panorama-display/ → gallery/ with prefix
    pd = ROOT / "panorama-display"
    if pd.is_dir():
        for f in sorted(pd.glob("*.yaml")):
            new_name = f.name if f.name.startswith("panorama_") else f"panorama_{f.name}"
            queue(f, ROOT / "gallery" / new_name)

    return moves


def execute(moves: list[tuple[Path, Path, str]], dry_run: bool) -> None:
    for src, dst, action in moves:
        rel_src = src.relative_to(ROOT.parent)
        rel_dst = dst.relative_to(ROOT.parent)
        prefix = "DRY" if dry_run else action.upper()
        if action == "rm":
            print(f"{prefix}  RM (dup of) {rel_dst}: {rel_src}")
            if not dry_run:
                src.unlink()
        else:
            print(f"{prefix}  {rel_src}  ->  {rel_dst}")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))


def cleanup_empty_dirs(dry_run: bool) -> None:
    """Remove now-empty source folders."""
    candidates = [
        "styles", "navigation_footer", "titlebar",
        "team_about", "counter-up", "panorama-display",
        *FOLDER_RENAMES.keys(),
    ]
    for name in candidates:
        d = ROOT / name
        if d.is_dir() and not any(d.iterdir()):
            print(f"{'DRY' if dry_run else 'RM '}  empty dir {d.name}/")
            if not dry_run:
                d.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    moves = plan_moves()
    if not moves:
        print("Nothing to move.")
        return 0

    print(f"Planned {len(moves)} moves\n")
    execute(moves, args.dry_run)
    print()
    cleanup_empty_dirs(args.dry_run)
    print(f"\n{'(dry run, no changes made)' if args.dry_run else 'done'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
