#!/bin/bash
# Norosera — Otomatik lint/format (PostToolUse hook)
# Write/Edit sonrasi degistirilen dosyayi otomatik formatlar.

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Python dosyalari -> ruff
if echo "$FILE_PATH" | grep -qE '\.py$'; then
    RUFF="$PROJECT_ROOT/backend/.venv/bin/ruff"
    if [ -x "$RUFF" ]; then
        $RUFF check --fix --quiet "$FILE_PATH" 2>/dev/null
        $RUFF format --quiet "$FILE_PATH" 2>/dev/null
    fi
fi

# TypeScript/JavaScript dosyalari -> eslint
if echo "$FILE_PATH" | grep -qE '\.(ts|tsx|js|jsx)$'; then
    ESLINT="$PROJECT_ROOT/frontend/node_modules/.bin/eslint"
    if [ -x "$ESLINT" ]; then
        $ESLINT --fix --quiet "$FILE_PATH" 2>/dev/null
    fi
fi

# CSS dosyalari -> prettier
if echo "$FILE_PATH" | grep -qE '\.css$'; then
    PRETTIER="$PROJECT_ROOT/frontend/node_modules/.bin/prettier"
    if [ -x "$PRETTIER" ]; then
        $PRETTIER --write --log-level silent "$FILE_PATH" 2>/dev/null
    fi
fi

exit 0
