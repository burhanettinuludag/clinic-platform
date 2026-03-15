#!/bin/bash
# PostToolUse hook: Auto-lint modified files

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Python files → ruff
if echo "$FILE_PATH" | grep -qE "\.py$"; then
    if command -v ruff &> /dev/null; then
        ruff check --fix "$FILE_PATH" 2>/dev/null
        ruff format "$FILE_PATH" 2>/dev/null
    fi
fi

# TypeScript/JavaScript → eslint + prettier
if echo "$FILE_PATH" | grep -qE "\.(ts|tsx|js|jsx)$"; then
    if [ -f "frontend/node_modules/.bin/eslint" ]; then
        cd frontend && npx eslint --fix "../$FILE_PATH" 2>/dev/null
    fi
fi

# CSS/Tailwind files
if echo "$FILE_PATH" | grep -qE "\.css$"; then
    if command -v prettier &> /dev/null; then
        prettier --write "$FILE_PATH" 2>/dev/null
    fi
fi

exit 0
