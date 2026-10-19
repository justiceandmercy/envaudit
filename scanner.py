"""Scanning helpers for envaudit."""
import re
from pathlib import Path

ENV_REF_PATTERNS = [
    re.compile(r'os\.environ\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]'),
    re.compile(r'os\.environ(?:\.get)?\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']'),
    re.compile(r'os\.getenv\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']'),
    re.compile(r'process\.env\.([A-Za-z_][A-Za-z0-9_]*)'),
    re.compile(r'process\.env\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]'),
    re.compile(r'os\.Getenv\(\s*"([A-Za-z_][A-Za-z0-9_]*)"'),
    re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}'),
    re.compile(r'(?<![A-Za-z0-9_])\$([A-Za-z_][A-Za-z0-9_]*)'),
    re.compile(r'env\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']'),
    re.compile(r'getenv\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']'),
]

SOURCE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".sh", ".bash",
               ".zsh", ".yml", ".yaml", ".toml", ".json", ".rb", ".php"}

SKIP_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__",
             "dist", "build", ".tox", "target"}


def parse_env_file(path):
    result = {}
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key and not key.startswith("#") and key.replace("_", "").isalnum():
                result[key] = value.strip().strip('"').strip("'")
    except (OSError, UnicodeDecodeError):
        pass
    return result


def find_env_files(root):
    root = Path(root)
    found = []
    for name in (".env", ".env.local", ".env.development",
                 ".env.production", ".env.test"):
        p = root / name
        if p.is_file():
            found.append(p)
    for p in root.rglob(".env*"):
        if p.is_file() and p not in found:
            found.append(p)
    return sorted(set(found))


def scan_sources(root):
    refs = {}
    root = Path(root)
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in SOURCE_EXTS:
            # allow dotfiles like .env.example
            if not p.name.startswith(".env"):
                continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for pat in ENV_REF_PATTERNS:
            for m in pat.finditer(text):
                var = m.group(1)
                refs.setdefault(var, set()).add(str(p.relative_to(root)))
    return refs
