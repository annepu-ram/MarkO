from types import SimpleNamespace


def test_brand_wording_prompt_logs_and_returns_metadata(monkeypatch):
    from campaign import section_rag

    labels = []

    class FakeBackend:
        def generate(self, system, user_prompt, model_override=None, temperature_override=None):
            assert "Markdown only" in system
            assert "Reusable" in user_prompt or "reusable" in user_prompt
            return "Use concise, confident wording."

    brand = SimpleNamespace(
        id="brand-1",
        org_id="org-1",
        to_generation_context=lambda: {
            "business_name": "Acme",
            "tone": "confident",
            "social_links": {"linkedin": "https://linkedin.com/company/acme"},
        },
    )

    monkeypatch.setattr(section_rag, "CampaignModelBackend", lambda: FakeBackend())
    monkeypatch.setattr(section_rag, "log_campaign_prompt", lambda label, system, user_prompt, metadata=None: labels.append(("prompt", label)))
    monkeypatch.setattr(section_rag, "log_campaign_output", lambda label, output, metadata=None: labels.append(("output", label)))

    prompt, metadata = section_rag.generate_brand_content_wording_prompt(
        brand,
        site_shell_config={
            "source": "brand_site_shell",
            "site_id": "site-1",
            "theme": {"colors": {"primary": "#111111"}, "fonts": {"heading": "Inter"}},
        },
        org_id="org-1",
    )

    assert prompt == "Use concise, confident wording."
    assert metadata["compiler"] == section_rag.BRAND_WORDING_PROMPT_COMPILER
    assert metadata["site_shell"]["site_id"] == "site-1"
    assert ("prompt", "BRAND_WORDING") in labels
    assert ("output", "BRAND_WORDING") in labels
