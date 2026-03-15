#!/bin/bash
# PostToolUse hook: Verify Django migration was actually created

INPUT=$(cat)
OUTPUT=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_result', {}).get('stdout', ''))
" 2>/dev/null)

if echo "$OUTPUT" | grep -q "No changes detected"; then
    echo "[MIGRATION] No migration needed — model changes may not be saved." >> /tmp/norosera-hook-log.txt
elif echo "$OUTPUT" | grep -q "Migrations for"; then
    echo "[MIGRATION] ✅ Migration created successfully." >> /tmp/norosera-hook-log.txt
    # Auto-run migrate check
    python3 backend/manage.py migrate --check 2>/dev/null
fi

exit 0
