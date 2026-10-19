"""Tests for envaudit."""
import tempfile
from pathlib import Path

from scanner import parse_env_file, scan_sources, find_env_files


def test_parse_env_basic():
    d = Path(tempfile.mkdtemp())
    f = d / ".env"
    f.write_text("FOO=bar\n# comment\nBAZ=1\nEMPTY=\n")
    assert parse_env_file(f) == {"FOO": "bar", "BAZ": "1", "EMPTY": ""}


def test_parse_env_quoted():
    d = Path(tempfile.mkdtemp())
    f = d / ".env"
    f.write_text('TOKEN="abc123"\nNAME=\'hello world\'\n')
    assert parse_env_file(f) == {"TOKEN": "abc123", "NAME": "hello world"}


def test_scan_python():
    d = Path(tempfile.mkdtemp())
    (d / "app.py").write_text(
        'import os\nx = os.environ["FOO"]\ny = os.getenv("BAR")\n'
        'z = os.environ.get("BAZ")\n')
    refs = scan_sources(d)
    assert {"FOO", "BAR", "BAZ"} <= set(refs)


def test_scan_javascript():
    d = Path(tempfile.mkdtemp())
    (d / "app.js").write_text(
        'const a = process.env.API_KEY;\n'
        'const b = process.env["SECRET"];\n')
    refs = scan_sources(d)
    assert "API_KEY" in refs and "SECRET" in refs


def test_scan_shell():
    d = Path(tempfile.mkdtemp())
    (d / "run.sh").write_text('#!/bin/sh\necho $HOME_DIR\necho ${PORT}\n')
    refs = scan_sources(d)
    assert "HOME_DIR" in refs and "PORT" in refs


def test_find_env_files():
    d = Path(tempfile.mkdtemp())
    (d / ".env").write_text("A=1\n")
    (d / ".env.local").write_text("B=2\n")
    found = find_env_files(d)
    names = {p.name for p in found}
    assert {".env", ".env.local"} <= names


def test_skips_node_modules():
    d = Path(tempfile.mkdtemp())
    nm = d / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("process.env.SHOULD_SKIP\n")
    (d / "main.js").write_text("process.env.KEEP\n")
    refs = scan_sources(d)
    assert "KEEP" in refs
    assert "SHOULD_SKIP" not in refs
