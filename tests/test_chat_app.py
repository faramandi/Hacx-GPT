"""Tests for the ``ChatApp`` controller."""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def app(hacx, monkeypatch):
    monkeypatch.setattr(hacx.time, "sleep", lambda *_: None)
    application = hacx.ChatApp()
    application.ui = MagicMock()
    return application


def test_init_defaults(hacx):
    application = hacx.ChatApp()
    assert application.llm_client is None
    assert application.ui is not None


def test_setup_no_key_user_declines(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: None)
    app.ui.get_input.return_value = "n"
    assert app._setup() is False


def test_setup_no_key_user_accepts_configures(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: None)
    app.ui.get_input.return_value = "y"
    app._configure_key = MagicMock(return_value=True)
    assert app._setup() is True
    app._configure_key.assert_called_once()


def test_setup_valid_key_verifies(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: "sk-or-valid")
    fake_llm = MagicMock()
    monkeypatch.setattr(hacx, "LLMClient", MagicMock(return_value=fake_llm))
    assert app._setup() is True
    fake_llm.client.models.list.assert_called_once()
    assert app.llm_client is fake_llm


def test_setup_invalid_key_reconfigures(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: "sk-or-bad")
    err = hacx.openai.AuthenticationError.__new__(hacx.openai.AuthenticationError)
    Exception.__init__(err, "bad")
    fake_llm = MagicMock()
    fake_llm.client.models.list.side_effect = err
    monkeypatch.setattr(hacx, "LLMClient", MagicMock(return_value=fake_llm))
    app.ui.get_input.return_value = "y"
    app._configure_key = MagicMock(return_value=True)
    assert app._setup() is True
    app._configure_key.assert_called_once()


def test_setup_invalid_key_declined_returns_false(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: "sk-or-bad")
    err = hacx.openai.AuthenticationError.__new__(hacx.openai.AuthenticationError)
    Exception.__init__(err, "bad")
    fake_llm = MagicMock()
    fake_llm.client.models.list.side_effect = err
    monkeypatch.setattr(hacx, "LLMClient", MagicMock(return_value=fake_llm))
    app.ui.get_input.return_value = "n"
    assert app._setup() is False


def test_setup_generic_error_returns_false(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "load_dotenv", lambda **_: None)
    monkeypatch.setattr(hacx.os, "getenv", lambda *_: "sk-or-x")
    monkeypatch.setattr(hacx, "LLMClient", MagicMock(side_effect=RuntimeError("nope")))
    assert app._setup() is False


def test_configure_key_empty_returns_false(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "pwinput", lambda **_: "")
    assert app._configure_key() is False


def test_configure_key_saves_and_exits(hacx, app, monkeypatch):
    monkeypatch.setattr(hacx, "pwinput", lambda **_: "sk-or-new")
    saved = {}
    monkeypatch.setattr(hacx, "set_key", lambda f, k, v: saved.update({"f": f, "k": k, "v": v}))
    with pytest.raises(SystemExit):
        app._configure_key()
    assert saved == {"f": hacx.Config.ENV_FILE, "k": hacx.Config.API_KEY_NAME, "v": "sk-or-new"}


def test_start_chat_requires_client(app):
    app.llm_client = None
    app._start_chat()
    app.ui.display_message.assert_called_once()


def test_start_chat_help_then_exit(app):
    app.llm_client = MagicMock()
    app.ui.get_input.side_effect = ["/help", "/exit"]
    app._start_chat()
    titles = [c.args[0] for c in app.ui.display_message.call_args_list]
    assert "Help" in titles


def test_start_chat_new_clears_history(app):
    app.llm_client = MagicMock()
    app.ui.get_input.side_effect = ["/new", "/exit"]
    app._start_chat()
    app.llm_client.clear_history.assert_called_once()


def test_start_chat_empty_prompt_skipped(app):
    app.llm_client = MagicMock()
    app.ui.get_input.side_effect = ["", "/exit"]
    app._start_chat()
    app.llm_client.get_streamed_response.assert_not_called()


def test_start_chat_normal_prompt_streams(app):
    app.llm_client = MagicMock()
    app.llm_client.get_streamed_response.return_value = iter(["response"])
    app.ui.get_input.side_effect = ["tell me something", "/exit"]
    app._start_chat()
    app.llm_client.get_streamed_response.assert_called_once_with("tell me something")
    app.ui.display_markdown_message.assert_called_once()


def test_about_us_waits_for_enter(app):
    app._about_us()
    app.ui.display_banner.assert_called_once()
    app.ui.get_input.assert_called_once()


def test_run_setup_fails_exits(app):
    app._setup = MagicMock(return_value=False)
    with pytest.raises(SystemExit):
        app.run()


def test_run_menu_dispatch_and_exit(app):
    app._setup = MagicMock(return_value=True)
    app._start_chat = MagicMock()
    app._about_us = MagicMock()
    # invalid option, then chat, then about, then exit
    app.ui.get_input.side_effect = ["9", "1", "3", "4"]
    app.run()
    app._start_chat.assert_called_once()
    app._about_us.assert_called_once()


def test_run_configure_option(app):
    app._setup = MagicMock(return_value=True)
    app._configure_key = MagicMock()
    app.ui.get_input.side_effect = ["2", "4"]
    app.run()
    app._configure_key.assert_called_once()
