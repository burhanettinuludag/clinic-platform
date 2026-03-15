#!/bin/bash
# Norosera — Tehlikeli komutlari engelle (PreToolUse hook)
# Bash tool cagrilarinda calisir, tehlikeli pattern'leri bloklar.

# stdin'den tool event JSON'unu oku
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [ -z "$COMMAND" ]; then
    exit 0
fi

# Kesinlikle engellenen komutlar
BLOCKED_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \."
    "git push --force"
    "git push -f "
    "DROP TABLE"
    "DROP DATABASE"
    "TRUNCATE "
    "DELETE FROM.*WHERE 1"
    "chmod 777"
    "curl.*\| bash"
    "curl.*\|bash"
    "wget.*\| bash"
    "wget.*\|bash"
    "manage.py flush"
    "python3 manage.py flush"
    "> /dev/sda"
    "mkfs\."
    "dd if="
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "BLOCKED: Tehlikeli komut engellendi: $pattern" >&2
        echo "$(date '+%Y-%m-%d %H:%M:%S') BLOCKED: $COMMAND" >> /tmp/norosera-hook-log.txt
        echo '{"decision": "block", "reason": "Tehlikeli komut engellendi: '"$pattern"'"}'
        exit 0
    fi
done

# Uyari verilenler (izin verilir ama loglanir)
WARN_PATTERNS=(
    "manage.py migrate"
    "docker compose down"
    "docker-compose down"
    "git reset"
    "git checkout -- "
    "git clean"
    "git stash drop"
)

for pattern in "${WARN_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: $COMMAND" >> /tmp/norosera-hook-log.txt
    fi
done

exit 0
