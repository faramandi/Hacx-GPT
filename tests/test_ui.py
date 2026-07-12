"""Tests for the ``UI`` class (terminal rendering helpers)."""
from unittest.mock import MagicMock


def test_clear_screen_delegates_to_console(hacx):
    ui = hacx.UI()
    ui.console = MagicMock()
    ui.clear_screen()
    ui.console.clear.assert_called_once()


def test_get_input_delegates_to_console(hacx):
    ui = hacx.UI()
    ui.console = MagicMock()
    ui.console.input.return_value = "typed value"
    result = ui.get_input("You")
    assert result == "typed value"
    assert ui.console.input.call_count == 1
    assert "You" in ui.console.input.call_args.args[0]


def test_display_message_renders_title_and_body(hacx, string_console):
    console, buffer = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_message("System", "hello world", "green")
    output = buffer.getvalue()
    assert "System" in output
    assert "hello world" in output


def test_display_banner_outputs_info_line(hacx, string_console):
    console, buffer = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_banner()
    assert "Developed by BlackTechX" in buffer.getvalue()


def test_display_main_menu_lists_options(hacx, string_console):
    console, buffer = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_main_menu()
    output = buffer.getvalue()
    assert "Main Menu" in output
    assert "Start Chat with HacxGPT" in output
    assert "Configure API Key" in output


def test_display_markdown_message_strips_prefix(hacx, string_console):
    console, buffer = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_markdown_message("HacxGPT", iter(["[HacxGPT]: ", "hello ", "there"]))
    output = buffer.getvalue()
    assert "hello there" in output
    assert "[HacxGPT]:" not in output


def test_display_markdown_message_empty_stream_shows_fallback(hacx, string_console):
    console, buffer = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_markdown_message("HacxGPT", iter([]))
    assert "No response received" in buffer.getvalue()


def test_display_markdown_message_error_stream_shows_one_error(hacx, string_console):
    console, _ = string_console
    ui = hacx.UI()
    ui.console = console
    ui.display_message = MagicMock()

    def failed_stream():
        raise hacx.LLMResponseError("The API request failed. Please try again.")
        yield

    ui.display_markdown_message("HacxGPT", failed_stream())
    ui.display_message.assert_called_once_with(
        "HacxGPT",
        "The API request failed. Please try again.",
        "red",
    )
