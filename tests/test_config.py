"""Tests for the module-level provider table and the ``Config`` class."""


def test_providers_table_structure(hacx):
    assert set(hacx._PROVIDERS) == {"openrouter", "deepseek"}
    for settings in hacx._PROVIDERS.values():
        assert settings["BASE_URL"].startswith("https://")
        assert settings["MODEL_NAME"]


def test_active_provider_is_supported(hacx):
    assert hacx.API_PROVIDER in hacx._PROVIDERS


def test_config_mirrors_active_provider(hacx):
    active = hacx._PROVIDERS[hacx.API_PROVIDER]
    assert hacx.Config.BASE_URL == active["BASE_URL"]
    assert hacx.Config.MODEL_NAME == active["MODEL_NAME"]


def test_config_constants(hacx):
    assert hacx.Config.API_KEY_NAME == "HacxGPT-API"
    assert hacx.Config.ENV_FILE == ".hacx"
    assert hacx.Config.CODE_THEME == "monokai"


def test_config_colors_are_strings(hacx):
    colors = hacx.Config.colors
    for name in [
        "TITLE",
        "PROMPT_BORDER",
        "PROMPT_TEXT",
        "ASSISTANT_BORDER",
        "ASSISTANT_TEXT",
        "INFO_BORDER",
        "WARNING_BORDER",
        "ERROR_BORDER",
        "SYSTEM_TEXT",
        "RESET",
    ]:
        assert isinstance(getattr(colors, name), str)
