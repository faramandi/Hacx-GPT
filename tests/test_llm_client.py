"""Tests for ``LLMClient`` (API history management and streaming)."""
from unittest.mock import MagicMock

import pytest

from conftest import make_chunk


@pytest.fixture
def patched_openai(hacx, monkeypatch):
    """Patch ``openai.OpenAI`` so no real client/network is created."""
    fake_client = MagicMock()
    factory = MagicMock(return_value=fake_client)
    monkeypatch.setattr(hacx.openai, "OpenAI", factory)
    return factory, fake_client


@pytest.fixture
def client(hacx, patched_openai):
    factory, fake_client = patched_openai
    ui = MagicMock()
    llm = hacx.LLMClient("sk-test-123", ui)
    llm._factory = factory
    llm._fake_client = fake_client
    llm._ui = ui
    return llm


def test_init_seeds_system_prompt(hacx, client):
    assert len(client.history) == 1
    assert client.history[0]["role"] == "system"
    assert client.history[0]["content"] == hacx.LLMClient.HACX_SYSTEM_PROMPT


def test_init_passes_credentials_and_headers(hacx, client):
    _, kwargs = client._factory.call_args
    assert kwargs["api_key"] == "sk-test-123"
    assert kwargs["base_url"] == hacx.Config.BASE_URL
    assert "HTTP-Referer" in kwargs["default_headers"]
    assert kwargs["default_headers"]["X-Title"] == "HacxGPT-CLI"


def test_clear_history_resets_and_notifies(client):
    client.history.append({"role": "user", "content": "hi"})
    client.clear_history()
    assert len(client.history) == 1
    assert client.history[0]["role"] == "system"
    assert client._ui.display_message.call_count == 1


def test_stream_handler_yields_and_records(client):
    stream = [make_chunk("Hello "), make_chunk("world"), make_chunk(None)]
    chunks = list(client._stream_handler(stream))
    assert chunks == ["Hello ", "world"]
    assert client.history[-1] == {"role": "assistant", "content": "Hello world"}


def test_stream_handler_empty_does_not_record(client):
    before = len(client.history)
    chunks = list(client._stream_handler([make_chunk(None), make_chunk("")]))
    assert chunks == []
    assert len(client.history) == before


def test_get_streamed_response_success(client):
    client._fake_client.chat.completions.create.return_value = [
        make_chunk("foo"),
        make_chunk("bar"),
    ]
    out = "".join(client.get_streamed_response("prompt text"))
    assert out == "foobar"
    assert client.history[1] == {"role": "user", "content": "prompt text"}
    assert client.history[-1] == {"role": "assistant", "content": "foobar"}


def test_get_streamed_response_auth_error_pops_user(hacx, client):
    err = hacx.openai.AuthenticationError.__new__(hacx.openai.AuthenticationError)
    Exception.__init__(err, "invalid key")
    client._fake_client.chat.completions.create.side_effect = err
    out = list(client.get_streamed_response("prompt text"))
    assert out == []
    assert all(m["role"] != "user" for m in client.history)
    assert client._ui.display_message.call_count == 1


def test_get_streamed_response_generic_error_pops_user(client):
    client._fake_client.chat.completions.create.side_effect = RuntimeError("boom")
    out = list(client.get_streamed_response("prompt text"))
    assert out == []
    assert all(m["role"] != "user" for m in client.history)
    assert client._ui.display_message.call_count == 1
