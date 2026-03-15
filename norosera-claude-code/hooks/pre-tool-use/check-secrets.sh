#!/bin/bash
# PreToolUse hook: Scan file writes for secrets and KVKK violations

INPUT=$(cat)
CONTENT=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
content = data.get('tool_input', {}).get('content', '')
file_path = data.get('tool_input', {}).get('file_path', '')
print(f'{file_path}\n---\n{content}')
" 2>/dev/null)

# Secret patterns
SECRET_PATTERNS=(
    "DJANGO_SECRET_KEY\s*=\s*['\"]"
    "AWS_SECRET_ACCESS_KEY"
    "OPENAI_API_KEY\s*=\s*['\"]sk-"
    "ANTHROPIC_API_KEY\s*=\s*['\"]sk-ant-"
    "DATABASE_URL\s*=\s*['\"]postgres://"
    "password\s*=\s*['\"][^'\"]{8,}"
    "REDIS_URL\s*=\s*['\"]redis://"
    "SMTP_PASSWORD"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
        # Allow in .env.example with placeholder values
        if echo "$CONTENT" | grep -q "\.env\.example"; then
            continue
        fi
        echo '{"decision": "block", "reason": "🔐 BLOCKED: Olası secret/API key tespit edildi. Lütfen .env dosyasını kullanın, kodu değil."}' >&2
        exit 2
    fi
done

# KVKK sensitive data patterns (Turkish ID, phone, etc.)
KVKK_PATTERNS=(
    "[0-9]{11}"                    # TC Kimlik No pattern
    "tc_kimlik|tcno|tckn"
    "hasta_adi|patient_name.*=.*['\"]"
    "telefon.*=.*['\"][0-9]"
)

FILE_PATH=$(echo "$CONTENT" | head -1)

# Only check non-test, non-fixture files
if ! echo "$FILE_PATH" | grep -qE "(test_|fixture|mock|seed)"; then
    for pattern in "${KVKK_PATTERNS[@]}"; do
        if echo "$CONTENT" | grep -qiE "$pattern"; then
            echo "[KVKK-WARN] Potential patient data in: $FILE_PATH" >> /tmp/norosera-kvkk-log.txt
        fi
    done
fi

exit 0
