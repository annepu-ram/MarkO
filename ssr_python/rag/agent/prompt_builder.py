"""ssr_python/rag/agent/prompt_builder.py — Condensed system prompt + dynamic context assembly."""
import tiktoken

from rag.config import config
from rag.agent.query_analyzer import QueryIntent
from rag.agent.component_specs import build_component_specs, VALID_TOKENS
from rag.agent.prompt_loader import load_system, render_user

_enc = tiktoken.get_encoding("cl100k_base")


class PromptBuilder:
    def build(
        self,
        intent: QueryIntent,
        chunks: list[dict],
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
    ) -> tuple[str, str]:
        """Build (system_prompt, user_prompt) for the SLM.

        Returns a tuple so model_backend can pass them separately.
        """
        budget = self._get_budget(intent, current_yaml)

        ctx_parts = []
        tokens_used = 0
        for chunk in chunks:
            chunk_tokens = chunk.get("token_count", len(_enc.encode(chunk["content"])))
            if tokens_used + chunk_tokens > budget:
                break
            source = chunk.get("source_file", "unknown")
            ctx_parts.append(
                f"--- Example from: {source} ---\n{chunk['content']}"
            )
            tokens_used += chunk_tokens

        context_block = "\n\n".join(ctx_parts)

        comp_names = list(intent.component_filter) if intent.component_filter else []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            comp_names.extend(meta.get("component_types", []))
        if not comp_names:
            comp_names = ["heading", "paragraph", "button", "image"]
        comp_specs = build_component_specs(comp_names)

        system = load_system("condensed")
        user_prompt = render_user("condensed",
            comp_specs=comp_specs,
            valid_tokens=VALID_TOKENS,
            context_block=context_block,
            current_yaml=current_yaml,
            selected_component=selected_component,
            message=message,
        )
        return system, user_prompt

    def _get_budget(self, intent: QueryIntent, current_yaml: str | None) -> int:
        """Dynamic token budget — reserve room for existing YAML in modify tasks."""
        if intent.action == "create_page":
            return config.context_budget_create_page
        if intent.action == "modify" and current_yaml:
            yaml_tokens = len(_enc.encode(current_yaml))
            return max(config.min_context_budget, config.context_budget_modify - yaml_tokens // 2)
        if intent.action == "create_section":
            return config.context_budget_create_section
        return config.context_budget_default
