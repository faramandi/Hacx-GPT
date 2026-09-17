---
name: testing-hacx-gpt-cli
description: Test HacxGPT's interactive CLI, provider setup, streaming, and error paths end-to-end.
---

# Testing HacxGPT CLI

## Devin Secrets Needed

- `OPENROUTER_HACX_TEST_API_KEY` — session-only OpenRouter key for live startup and chat requests.
- `DEEPSEEK_HACX_TEST_API_KEY` — optional when testing the DeepSeek provider.

Never print a key, commit `.hacx`, or include key values in screenshots, recordings, logs, or reports.

## Environment

```bash
python3 -m venv ~/.venvs/Hacx-GPT
~/.venvs/Hacx-GPT/bin/python -m pip install -r requirements-dev.txt
```

Validated non-interactive checks:

```bash
~/.venvs/Hacx-GPT/bin/python -m pytest -q
~/.venvs/Hacx-GPT/bin/python -m py_compile HacxGPT.py
bash -n install.sh
```

## Live key setup

The CLI reads `.hacx` through `python-dotenv` using the variable `HacxGPT-API`. The file is gitignored.

```bash
printf 'HacxGPT-API=%s\n' "$OPENROUTER_HACX_TEST_API_KEY" > .hacx
```

OpenRouter access is API-key based; no browser login is needed. The key should permit `models.list()` and chat-completion requests.

## Interactive runtime test

Run the user-facing CLI in a maximized terminal:

```bash
~/.venvs/Hacx-GPT/bin/python HacxGPT.py
```

Primary flow:

1. Confirm a valid key reaches the main menu.
2. Select `1`, send a short harmless prompt, and verify either a streamed response or one specific **API Error** panel.
3. After an API error, verify the `You:` prompt reappears with no traceback or duplicate empty-response message.
4. Enter `/new`; verify `New chat session started.` renders and the prompt remains interactive.
5. Enter `/exit`, return to the menu, and choose `4`.

The configured provider model might become unavailable or rate-limited. Treat a live 404/429 as a valid error-path test, report the provider limitation, and do not silently commit a different model. A temporary model edit for a happy-path regression must be clearly labeled and reverted.

## Missing-key test

Temporarily move `.hacx`, run the CLI, decline configuration, and capture the exit code:

```bash
mv .hacx .hacx.test
~/.venvs/Hacx-GPT/bin/python HacxGPT.py
echo "$?"
mv .hacx.test .hacx
```

Expected behavior: **Setup Required**, no main menu, and exit code `1`.

## Evidence and cleanup

- Record interactive terminal tests and annotate startup, error rendering, recovery, and exit status.
- Capture full-screen screenshots of pass/fail states.
- Restore or remove temporary `.hacx` files.
- Confirm `git status --short` is clean before reporting.
