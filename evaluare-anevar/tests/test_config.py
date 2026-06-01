from evaluare.config import load_env_file, Settings


def test_load_env_file_sets_environ(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=sk-test-123\nNARRATIVE_MODEL=claude-sonnet-4-6\n",
                   encoding="utf-8")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    load_env_file(env)
    import os
    assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-123"


def test_settings_without_key_has_no_client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = Settings.from_env()
    assert s.api_key is None
    assert s.narrative_client() is None      # fallback: fara AI


def test_settings_with_key_builds_client(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    s = Settings.from_env()
    assert s.api_key == "sk-test-123"
    client = s.narrative_client()
    # construit, dar fara apel real (constructorul nu face request)
    assert client is not None
    assert client.__class__.__name__ == "AnthropicNarrativeClient"


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("NARRATIVE_MODEL", raising=False)
    s = Settings.from_env()
    assert s.model == "claude-sonnet-4-6"


def test_settings_perplexity_cand_lipseste_anthropic(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("PERPLEXITY_API_KEY", "pplx-test")
    s = Settings.from_env()
    client = s.narrative_client()
    assert client is not None
    assert client.__class__.__name__ == "PerplexityNarrativeClient"


def test_anthropic_are_prioritate(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "pplx-test")
    s = Settings.from_env()
    assert s.narrative_client().__class__.__name__ == "AnthropicNarrativeClient"
