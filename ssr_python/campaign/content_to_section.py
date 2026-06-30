"""Compile content library items into campaign-section renderer YAML."""

from campaign.section_rag import (
    CAMPAIGN_SECTION_COMPILER as AGENT_COMPILER_VERSION,
    build_section_context as _build_agent_section_context,
    generate_section_yaml as generate_section_yaml_with_agents,
)


def compile_content_to_section_yaml(section_type, items, *, brand=None, product=None, site_shell_config=None, generation_mode="agent", section_metadata=None):
    """Return ``(yaml_text, metadata)`` for a SectionItem built from ContentItems."""
    if (generation_mode or "agent") != "agent":
        raise ValueError("Only RAG agent section generation is supported.")
    return generate_section_yaml_with_agents(
        section_type,
        items,
        brand=brand,
        product=product,
        site_shell_config=site_shell_config,
        section_metadata=section_metadata,
    )
