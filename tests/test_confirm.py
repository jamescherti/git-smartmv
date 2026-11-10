#!/usr/bin/env python

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from git_smartmv import Smartmv


def test_confirm_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert Smartmv.confirm("Execute? [y,n] ") is True


def test_confirm_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert Smartmv.confirm("Execute? [y,n] ") is False


def test_confirm_eof_is_no(monkeypatch):
    """Piped/closed stdin must not crash with a traceback (EOFError)."""

    def _raise_eof(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise_eof)
    assert Smartmv.confirm("Execute? [y,n] ") is False
