#!/bin/bash
# PreToolUse hook: Block dangerous commands deterministically
# Claude Code passes event JSON on stdin

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
cmd = data.get('tool_input', {}).get('command', '')
print(cmd)
" 2>/dev/null)

# Dangerous patterns - BLOCK unconditionally
BLOCKED_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \."
    "git push --force"
    "git push -f"
    "DROP TABLE"
    "DROP DATABASE"
    "TRUNCATE"
    "DELETE FROM.*WHERE 1"
    "chmod 777"
    "curl.*| bash"
    "wget.*| bash"
    "python manage.py flush"
    "> /dev/sda"
    "mkfs"
    "dd if="
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo '{"decision": "block", "reason": "🚫 BLOCKED: Tehlikeli komut tespit edildi: '"$pattern"'. Bu komut Norosera güvenlik politikası tarafından engellenmiştir."}' >&2
        exit 2
    fi
done

# Warn on sensitive patterns (allow but log)
WARN_PATTERNS=(
    "manage.py migrate"
    "docker-compose down"
    "npm run build"
    "git reset"
    "git checkout.*--"
)

for pattern in "${WARN_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "[WARN] Sensitive command detected: $COMMAND" >> /tmp/norosera-hook-log.txt
    fi
done

exit 0
