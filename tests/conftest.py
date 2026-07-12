"""Shared pytest fixtures and helpers for the HacxGPT test suite.

``HacxGPT.py`` lives at the repository root and is not part of an installable
package, so we add the repo root to ``sys.path`` and import it by module name.
"""
import io
import os
import sys
from types import SimpleNamespace

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import HacxGPT  # noqa: E402


@pytest.fixture
def hacx():
    """The imported HacxGPT module under test."""
    return HacxGPT


@pytest.fixture
def string_console():
    """A ``rich`` Console that writes to an in-memory buffer.

    Returns a ``(console, buffer)`` tuple so tests can assert on rendered text.
    """
    buffer = io.StringIO()
    console = HacxGPT.Console(file=buffer, force_terminal=False, width=100)
    return console, buffer


def make_chunk(content):
    """Build a fake OpenAI streaming chunk exposing ``choices[0].delta.content``."""
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=content))])
