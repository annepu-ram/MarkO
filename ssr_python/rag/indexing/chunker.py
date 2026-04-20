"""ssr_python/rag/indexing/chunker.py — YAML-aware + markdown chunking."""
import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path

from rag.config import config


@dataclass
class Chunk:
    id: str                    # Unique: "{source_file}::{chunk_index}"
    content: str               # Raw YAML/markdown fragment
    context_header: str        # Parent context for embedding enrichment
    content_with_context: str  # context_header + content (used for embedding)
    source_file: str
    doc_type: str              # template | template_section | template_full_page | outline | guide | config
    metadata: dict             # Component types, industry, section, etc.
    token_count: int


@dataclass
class FileComments:
    """Structured header comments extracted from YAML template files.

    Parses patterns like:
        # Full-Screen Immersive Hero
        # A dramatic, full-screen hero with stunning background imagery
        # Base components: image, layout-column, layout-row, paragraph, heading, button
        # Section type: hero
        # Layout: fullscreen
        # Visual style: monochrome, dark_mode
        # Perfect for: Travel, hospitality, luxury brands, creative agencies
    """
    title: str = ""            # First comment line
    description: str = ""      # Descriptive line (not title, not "Perfect for:")
    use_cases: str = ""        # "Perfect for:" industries/scenarios
    visual_style: str = ""     # "Visual style:" tag (glassmorphism, modern, etc.)
    base_components: str = ""  # "Base components:" component list
    section_type: str = ""     # "Section type:" section classification
    layout: str = ""           # "Layout:" layout pattern
    raw_lines: list = field(default_factory=list)

    def as_context(self) -> str:
        """Format as context string for embedding enrichment."""
        parts = []
        if self.title:
            parts.append(f"Template: {self.title}")
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.section_type:
            parts.append(f"Section: {self.section_type}")
        if self.layout:
            parts.append(f"Layout: {self.layout}")
        if self.base_components:
            parts.append(f"Components: {self.base_components}")
        if self.use_cases:
            parts.append(f"Use cases: {self.use_cases}")
        if self.visual_style:
            parts.append(f"Visual style: {self.visual_style}")
        return " | ".join(parts) if parts else ""

    def as_metadata(self) -> dict:
        """Return comment fields as a dict for chunk metadata."""
        d = {}
        if self.title:
            d["template_title"] = self.title
        if self.description:
            d["template_description"] = self.description
        if self.use_cases:
            d["template_use_cases"] = self.use_cases
        if self.visual_style:
            d["template_visual_style"] = self.visual_style
        if self.base_components:
            d["header_base_components"] = self.base_components
        if self.section_type:
            d["header_section_type"] = self.section_type
        if self.layout:
            d["header_layout"] = self.layout
        return d


# Top-level directories that should not be used as category names
_ROOT_DIRS = {"example_templates", "website_example_outlines"}


class DocumentChunker:
    """Routes documents to the right chunking strategy."""

    def chunk_file(self, file_path: Path) -> list[Chunk]:
        suffix = file_path.suffix.lower()
        content = file_path.read_text(encoding="utf-8")

        if suffix in (".yaml", ".yml"):
            return self._chunk_yaml_template(content, file_path)
        elif suffix == ".md":
            return self._chunk_markdown(content, file_path)
        else:
            return self._chunk_plain_text(content, file_path)

    # ── File Header Comment Extraction ──

    @staticmethod
    def _extract_file_comments(content: str) -> FileComments:
        """Extract structured metadata from YAML file header comments.

        Parses the leading comment block before the first YAML line.
        Recognizes patterns:
            # Title Line
            # Description line
            # Base components: image, heading, button
            # Section type: hero
            # Layout: fullscreen
            # Visual style: glassmorphism
            # Perfect for: industry1, industry2, ...
        """
        lines = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                # Strip leading '# ' or '#'
                text = stripped.lstrip("#").strip()
                if text:
                    lines.append(text)
            elif stripped == "":
                continue  # Skip blank lines between comments and YAML
            else:
                break  # Stop at first non-comment, non-blank line

        if not lines:
            return FileComments()

        title = lines[0]
        description = ""
        use_cases = ""
        visual_style = ""
        base_components = ""
        section_type = ""
        layout = ""

        for line in lines[1:]:
            lower = line.lower()
            # "Perfect for:" / "Use cases:" / "Best for:" prefix
            if lower.startswith("perfect for:"):
                use_cases = line[len("Perfect for:"):].strip().rstrip(".")
            elif lower.startswith("use cases:"):
                use_cases = line[len("Use cases:"):].strip().rstrip(".")
            elif lower.startswith("best for:"):
                use_cases = line[len("Best for:"):].strip().rstrip(".")
            elif lower.startswith("visual style:"):
                visual_style = line[len("Visual style:"):].strip()
            elif lower.startswith("base components:"):
                base_components = line[len("Base components:"):].strip()
            elif lower.startswith("section type:"):
                section_type = line[len("Section type:"):].strip()
            elif lower.startswith("layout:"):
                layout = line[len("Layout:"):].strip()
            elif not description and not lower.startswith("properties:") and not lower.startswith("key:"):
                # First non-tagged line = description
                description = line

        return FileComments(
            title=title,
            description=description,
            use_cases=use_cases,
            visual_style=visual_style,
            base_components=base_components,
            section_type=section_type,
            layout=layout,
            raw_lines=lines,
        )

    # ── Category Extraction ──

    @staticmethod
    def _extract_category(path: Path) -> str:
        """Return parent folder name as category (e.g., 'hero', 'pricing_plan_cards').

        Falls back to 'uncategorized' if parent is a root directory.
        """
        parent_name = path.parent.name
        if parent_name in _ROOT_DIRS or not parent_name:
            return "uncategorized"
        return parent_name

    # ── YAML Template Chunking ──

    def _chunk_yaml_template(self, content: str, path: Path) -> list[Chunk]:
        """Split YAML at top-level component boundaries.

        Each `- name:` block under `components:` becomes a chunk.
        Also creates a section-level chunk for the entire template.
        File header comments + site/page metadata enrich the context_header.
        """
        chunks = []

        # Extract file-level comments before YAML parsing
        file_comments = self._extract_file_comments(content)
        category = self._extract_category(path)

        try:
            doc = yaml.safe_load(content)
        except yaml.YAMLError:
            return self._chunk_yaml_by_regex(content, path, file_comments)

        if doc is None:
            return []

        # Extract site-level context (theme, fonts, colors)
        site_ctx = self._extract_site_context(doc)

        # SwiftSites YAML uses list root: [{name: site, components: [{name: page, ...}]}]
        site_node = doc[0] if isinstance(doc, list) else doc
        if not isinstance(site_node, dict):
            return self._chunk_yaml_by_regex(content, path, file_comments)

        # Handle page-root templates: if site_node IS a page, treat it as the only page
        if site_node.get("name") == "page":
            pages = [site_node]
        else:
            pages = [c for c in site_node.get("components", []) if isinstance(c, dict) and c.get("name") == "page"]

        # If no pages found, try treating the doc as a flat component list
        if not pages:
            components = site_node.get("components", [])
            if not components and isinstance(doc, list):
                components = doc
            return self._chunk_component_list(components, site_ctx, path, "root", file_comments, category)

        for page in pages:
            page_name = page.get("slug", page.get("title", "unknown"))
            components = page.get("components", [])

            # Component-level chunks
            chunks.extend(
                self._chunk_component_list(components, site_ctx, path, page_name, file_comments, category)
            )

            # Section-level chunk (complete section as one chunk)
            section_chunk = self._create_section_chunk(
                components, site_ctx, path, page_name, file_comments, category
            )
            if section_chunk:
                chunks.append(section_chunk)

            # Full-page chunk (includes site wrapper) for create_page intent
            if len(components) <= 8:
                full_yaml = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False)
                comment_ctx = file_comments.as_context()
                full_header = f"# FULL PAGE: {path.name} | {site_ctx}"
                if comment_ctx:
                    full_header = f"{full_header}\n# {comment_ctx}"

                meta = file_comments.as_metadata()
                meta["category"] = category

                chunks.append(Chunk(
                    id=f"{path.stem}::full_page",
                    content=full_yaml,
                    context_header=full_header,
                    content_with_context=f"{full_header}\n{full_yaml}",
                    source_file=str(path),
                    doc_type="template_full_page",
                    metadata=meta,
                    token_count=0,
                ))

        return chunks

    def _create_section_chunk(
        self, components: list, site_ctx: str, path: Path,
        page_name: str, file_comments: FileComments, category: str,
    ) -> Chunk | None:
        """Create a section-level chunk containing all components for the template.

        Used by create_section intent — provides complete section examples.
        """
        if not components:
            return None

        # Build rich context header for embedding
        header_parts = [f"# SECTION: {file_comments.title or path.stem}"]
        if file_comments.description:
            header_parts.append(f"# Description: {file_comments.description}")
        if file_comments.section_type:
            header_parts.append(f"# Section type: {file_comments.section_type}")
        if file_comments.layout:
            header_parts.append(f"# Layout: {file_comments.layout}")
        if file_comments.base_components:
            header_parts.append(f"# Components: {file_comments.base_components}")
        if file_comments.visual_style:
            header_parts.append(f"# Visual style: {file_comments.visual_style}")
        if file_comments.use_cases:
            header_parts.append(f"# Perfect for: {file_comments.use_cases}")
        header_parts.append(f"# Source: {category}/{path.name} | Category: {category}")
        header_parts.append(f"# Theme: {site_ctx}")
        header = "\n".join(header_parts)

        # Serialize components (without site wrapper)
        comp_yaml = yaml.dump(
            components, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

        # Truncate if exceeding max chars
        max_chars = config.section_chunk_max_chars
        if len(comp_yaml) > max_chars:
            truncated = comp_yaml[:max_chars]
            # Cut at last complete line
            last_newline = truncated.rfind("\n")
            if last_newline > max_chars // 2:
                truncated = truncated[:last_newline]
            comp_yaml = truncated + f"\n# ... (truncated, {len(components)} total components)"

        meta = file_comments.as_metadata()
        meta["category"] = category

        return Chunk(
            id=f"{path.stem}::section",
            content=comp_yaml,
            context_header=header,
            content_with_context=f"{header}\n{comp_yaml}",
            source_file=str(path),
            doc_type="template_section",
            metadata=meta,
            token_count=0,
        )

    def _chunk_component_list(
        self, components: list, site_ctx: str, path: Path, page_name: str,
        file_comments: FileComments, category: str,
    ) -> list[Chunk]:
        """Chunk a list of components into individual chunks."""
        comment_ctx = file_comments.as_context()
        comment_meta = file_comments.as_metadata()
        comment_meta["category"] = category

        chunks = []
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                continue
            comp_yaml = yaml.dump(
                [comp], default_flow_style=False, allow_unicode=True, sort_keys=False
            )

            # Build context header with file comments + theme + position
            header_parts = [f"# Source: {path.name} | Page: {page_name}"]
            if comment_ctx:
                header_parts.append(f"# {comment_ctx}")
            header_parts.append(f"# Theme: {site_ctx}")
            header_parts.append(f"# Component {i+1}/{len(components)}")
            header = "\n".join(header_parts)

            chunk_id = f"{path.stem}::p{page_name}::c{i}"

            chunks.append(Chunk(
                id=chunk_id,
                content=comp_yaml,
                context_header=header,
                content_with_context=f"{header}\n{comp_yaml}",
                source_file=str(path),
                doc_type="template",
                metadata=dict(comment_meta),  # Copy so each chunk gets its own dict
                token_count=0,
            ))
        return chunks

    def _extract_site_context(self, doc) -> str:
        """Pull theme info (colors, fonts) into a one-line summary."""
        site = doc[0] if isinstance(doc, list) else doc
        if not isinstance(site, dict):
            return "no-theme"
        props = site.get("properties", {})
        if not isinstance(props, dict):
            return "no-theme"
        theme = props.get("theme", {})
        if not isinstance(theme, dict):
            return "no-theme"
        colors = theme.get("colors", {})
        fonts = theme.get("fonts", {})
        if not isinstance(colors, dict):
            colors = {}
        if not isinstance(fonts, dict):
            fonts = {}
        primary = colors.get("primary", "?")
        bg = colors.get("background", "?")
        font = fonts.get("heading", fonts.get("content", "?"))
        return f"primary={primary} bg={bg} font={font}"

    # ── Markdown Chunking ──

    def _chunk_markdown(self, content: str, path: Path) -> list[Chunk]:
        """Split markdown at ## headings. Each section = one chunk."""
        sections = re.split(r'^(## .+)$', content, flags=re.MULTILINE)
        chunks = []
        current_heading = "Introduction"

        # Determine doc_type from path
        source_str = str(path).lower()
        if "style_themes" in source_str:
            doc_type = "style"
        elif "website_example_outlines" in source_str:
            doc_type = "outline"
        else:
            doc_type = "guide"

        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            if section.startswith("## "):
                current_heading = section.lstrip("# ").strip()
                continue

            chunk_id = f"{path.stem}::s{i}_{current_heading[:30]}"
            header = f"# Source: {path.name} | Section: {current_heading}"

            chunks.append(Chunk(
                id=chunk_id,
                content=section,
                context_header=header,
                content_with_context=f"{header}\n{section}",
                source_file=str(path),
                doc_type=doc_type,
                metadata={"section_heading": current_heading},
                token_count=0,
            ))

        return chunks

    def _chunk_yaml_by_regex(self, content: str, path: Path, file_comments: FileComments = None) -> list[Chunk]:
        """Fallback: split YAML at '- name:' lines if parsing fails."""
        if file_comments is None:
            file_comments = self._extract_file_comments(content)

        comment_ctx = file_comments.as_context()
        comment_meta = file_comments.as_metadata()
        category = self._extract_category(path)
        comment_meta["category"] = category

        blocks = re.split(r'(?=^- name:|\n  - name:)', content, flags=re.MULTILINE)
        chunks = []
        for i, block in enumerate(blocks):
            block = block.strip()
            if not block or len(block) < 20:
                continue
            chunk_id = f"{path.stem}::regex_{i}"

            header = f"# Source: {path.name} (regex split)"
            if comment_ctx:
                header = f"{header}\n# {comment_ctx}"

            chunks.append(Chunk(
                id=chunk_id,
                content=block,
                context_header=header,
                content_with_context=f"{header}\n{block}",
                source_file=str(path),
                doc_type="template",
                metadata=dict(comment_meta),
                token_count=0,
            ))
        return chunks

    def _chunk_plain_text(self, content: str, path: Path) -> list[Chunk]:
        """Fallback for non-YAML, non-markdown files."""
        if len(content.strip()) < 20:
            return []
        return [Chunk(
            id=f"{path.stem}::full",
            content=content,
            context_header=f"# Source: {path.name}",
            content_with_context=f"# Source: {path.name}\n{content}",
            source_file=str(path),
            doc_type="other",
            metadata={},
            token_count=0,
        )]
