#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
SKILL_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
REPO_ROOT=$(CDPATH= cd -- "$SKILL_ROOT/../.." && pwd -P)

PY=""

if [ -n "${PPT_MASTER_PYTHON:-}" ]; then
  PY="$PPT_MASTER_PYTHON"
elif [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PY="$REPO_ROOT/.venv/bin/python"
elif [ -x "$SKILL_ROOT/.venv/bin/python" ]; then
  PY="$SKILL_ROOT/.venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
  PY="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY=$(command -v python3)
fi

if [ -z "$PY" ] || [ ! -x "$PY" ]; then
  echo "PPT Master: no usable Python interpreter found." >&2
  echo "Create the repository .venv or set PPT_MASTER_PYTHON." >&2
  exit 2
fi

if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
  echo "PPT Master: Python 3.10+ is required; selected interpreter: $PY" >&2
  exit 2
fi

exec "$PY" "$@"
