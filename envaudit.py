#!/usr/bin/env python3
"""envaudit: audit environment variable usage in a codebase."""
import argparse
import json
import sys
from pathlib import Path

from scanner import parse_env_file, find_env_files, scan_sources


def main():
    ap = argparse.ArgumentParser(
        description="Audit environment variable usage against .env files.")
    ap.add_argument("path", nargs="?", default=".",
                    help="project root to scan (default: .)")
    ap.add_argument("--env", help="specific .env file to compare against")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when there are unused variables too")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"envaudit: not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    if args.env:
        env_files = [Path(args.env).resolve()]
    else:
        env_files = find_env_files(root)

    defined = {}
    for f in env_files:
        defined.update(parse_env_file(f))

    refs = scan_sources(root)

    missing = sorted(set(refs) - set(defined))
    unused = sorted(set(defined) - set(refs))
    ok = sorted(set(refs) & set(defined))

    if args.json:
        out = {
            "root": str(root),
            "env_files": [str(f) for f in env_files],
            "defined": sorted(defined),
            "referenced": sorted(refs),
            "missing": missing,
            "unused": unused,
            "used": ok,
            "files": {k: sorted(v) for k, v in refs.items()},
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"envaudit: scanned {root}")
        print(f"  env files: {', '.join(str(f) for f in env_files) or '(none)'}")
        print(f"  defined: {len(defined)}  referenced: {len(refs)}  "
              f"matched: {len(ok)}")
        if missing:
            print("\nMISSING (referenced in code but not defined):")
            for v in missing:
                print(f"  - {v}  ({', '.join(sorted(refs[v]))})")
        if unused:
            print("\nUNUSED (defined in .env but not referenced in code):")
            for v in unused:
                print(f"  - {v}")
        if not missing and not unused:
            print("\nOK: environment usage matches definitions.")

    code = 0
    if missing:
        code = 1
    if unused and args.strict:
        code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
