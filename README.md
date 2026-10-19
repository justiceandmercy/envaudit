# envaudit

Audit environment variable usage in a codebase: find variables referenced in
source code but missing from `.env`, and variables defined in `.env` but never
used. Zero dependencies, runs offline.

## Features

- Scans Python, JavaScript/TypeScript, Go, Ruby, PHP, shell, YAML, JSON and
  more for environment variable references.
- Parses `.env`, `.env.local`, `.env.*` files (quoted values supported).
- Reports **missing** (used in code, not defined) and **unused** (defined, not
  used) variables.
- Text or JSON output for CI integration.
- `--strict` mode fails the build on unused variables.
- Skips `node_modules`, `.git`, virtualenvs and build dirs.

## Install

No install needed. Requires Python 3.8+.

```sh
git clone https://github.com/yourname/envaudit.git
cd envaudit
```

Or copy `envaudit.py` and `scanner.py` into your project.

## Usage

```sh
# scan current directory
python3 envaudit.py

# scan a project
python3 envaudit.py ./my-app

# use a specific env file
python3 envaudit.py ./my-app --env ./my-app/.env.production

# JSON output (for CI)
python3 envaudit.py ./my-app --json

# strict: fail on unused too
python3 envaudit.py ./my-app --strict
```

Exit codes: `0` when usage matches definitions, `1` when there are missing
variables (or unused in `--strict` mode), `2` on usage errors.

## Example output

```
envaudit: scanned /app
  env files: /app/.env
  defined: 2  referenced: 2  matched: 1

MISSING (referenced in code but not defined):
  - MISSING_ONE  (main.py)

UNUSED (defined in .env but not referenced in code):
  - UNUSED_VAR
```

## License

MIT
