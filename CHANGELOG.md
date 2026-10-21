## [Unreleased]

### Added

- GitHub Actions CI running pytest on Python 3.10/3.11/3.12 and ruff lint.
- README badges for CI, license, release, Python support and stars.
- `SUPPORT.md` and `TREASURY.md` donation addresses.

### Changed

- README Quick Start now points at installing from Git, since the package is
  not published on PyPI yet.

### Fixed

- Removed unused imports in `agent_undo/rollback.py` (`difflib`, `textwrap`,
  `pathlib.Path`).
- Moved the mid-file `dataclasses` import in `agent_undo/rollback.py` to the
  top of the module, where it belongs.
- Dropped redundant `f` prefixes from f-strings without placeholders and
  wrapped over-long lines in `journal.py` and `rollback.py`.
- Removed an unused `cp_id` local and an unused `pathlib.Path` import in the
  test suite.

## [0.1.1] - 2026-10-21

### Security

- Rollback scripts now quote every path and encode file contents as base64, so
  a filename containing spaces, quotes or shell metacharacters can no longer
  break out of the generated `undo.sh` and execute arbitrary commands (#75,
  #78).
- `get_ops_since` uses `>=` so operations recorded in the same second as the
  checkpoint are no longer silently dropped from a rollback.

### Fixed

- `get_session_id()` creates the session file when it is missing or empty
  instead of crashing or returning an empty session id, which collided every
  operation in one session (#60, #66, #69).
- `DEFAULT_DB` is resolved at call time, not import time, so `agent-undo init`
  inside a different working directory journals the right database (#66).
- `agent-undo log` and `rollback` parse their CLI flags with
  `parse_intermixed_args`; on Python 3.10/3.11 they raised `SystemExit` instead
  of running, and a stray `--` token could be consumed as the database path
  (#53, #56, #57).
- The Bash pre-tool hook parses its JSON `tool_input`, so `git` commands are
  classified as `git` rather than `shell` (#55).
- Journal SQL quotes the reserved word `"timestamp"` in every statement (#73).
- `rollback --dry-run` without a checkpoint lists the whole session, and the
  diff preview prints real line numbers instead of a literal `@@` placeholder
  (#61, #62).
- README no longer offers `pip install agent-undo`, which cannot work while the
  package is unpublished; a regression test guards against reintroducing it
  (#59).
