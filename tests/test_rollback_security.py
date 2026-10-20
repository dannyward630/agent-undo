"""Security regressions for the generated rollback script (#75)."""

from __future__ import annotations

import subprocess

from agent_undo.journal import Journal
from agent_undo.rollback import RollbackGenerator


def test_quoted_path_cannot_inject_commands(tmp_path):
    """A path containing a single quote must not break out of the generated bash."""
    journal = Journal(tmp_path / "j.db")
    journal.record("s1", "file-write", path="/tmp/seed.txt", content_before="seed")
    journal.checkpoint("s1", "cp")
    pwned = tmp_path / "pwned"
    evil = tmp_path / "it's-a-file.txt"
    attacker = f"{evil}'$(touch {pwned})'.txt"
    journal.record("s1", "file-write", path=attacker, content_before="original")

    script = RollbackGenerator(journal).generate("s1", target_op_id=2)

    # The payload is still named in the script (as a comment), but the restore
    # commands must not hand it to the shell unquoted.
    assert attacker in script
    assert "$(touch" in script  # literal text, inside a quoted word
    proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert not pwned.exists(), "injected command executed!"


def test_newline_in_command_cannot_break_out_of_comment(tmp_path):
    journal = Journal(tmp_path / "j.db")
    journal.record("s1", "file-write", path="/tmp/seed.txt", content_before="seed")
    journal.checkpoint("s1", "cp")
    pwned = tmp_path / "pwned"
    journal.record(
        "s1",
        "shell",
        command=f"echo hi\ntouch {pwned}",
    )

    script = RollbackGenerator(journal).generate("s1", target_op_id=2)

    proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert not pwned.exists(), "newline in command broke out of the comment!"


def test_plain_path_still_restores_content(tmp_path):
    """The quoting fix must not break the normal restore path."""
    target = tmp_path / "real.txt"
    target.write_text("original")
    journal = Journal(tmp_path / "j.db")
    journal.record("s1", "file-write", path="/tmp/seed.txt", content_before="seed")
    journal.checkpoint("s1", "cp")
    journal.record("s1", "file-write", path=str(target), content_before="original")

    script = RollbackGenerator(journal).generate("s1", target_op_id=2)
    target.write_text("changed")

    proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert target.read_text() == "original"
