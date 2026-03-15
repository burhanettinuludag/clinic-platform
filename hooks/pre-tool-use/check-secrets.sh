#!/bin/bash
# Norosera — Secret ve KVKK veri sizintisi kontrolu (PreToolUse hook)
# Write/Edit tool cagrilarinda dosya icerigini tarar.

INPUT=$(cat)

# Dosya yolunu al
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

# .env.example ve test dosyalarini atla
if echo "$FILE_PATH" | grep -qiE '\.(env\.example|test|spec|fixture|mock|factory)'; then
    exit 0
fi

# Icerik satirlarini al (new_string veya content)
CONTENT=$(echo "$INPUT" | grep -oE '"(new_string|content)"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"[^"]*"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [ -z "$CONTENT" ]; then
    exit 0
fi

# Secret pattern'leri
SECRET_PATTERNS=(
    "DJANGO_SECRET_KEY\s*="
    "AWS_SECRET_ACCESS_KEY"
    "GROQ_API_KEY\s*="
    "GEMINI_API_KEY\s*="
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "DATABASE_URL\s*=\s*postgres"
    "REDIS_URL\s*=\s*redis"
    "SMTP_PASSWORD"
    "IYZICO_SECRET_KEY"
    "SENTRY_DSN\s*=\s*http"
    "password\s*=\s*['\"][^'\"]{8,}"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
        echo "BLOCKED: Secret/credential tespit edildi: $pattern" >&2
        echo "$(date '+%Y-%m-%d %H:%M:%S') SECRET_BLOCKED: $FILE_PATH - $pattern" >> /tmp/norosera-hook-log.txt
        echo '{"decision": "block", "reason": "Secret veya credential dosyaya yazilmak uzere: '"$pattern"'. Bunlari .env dosyasina koyun."}'
        exit 0
    fi
done

# KVKK hassas veri uyarisi (bloklamaz, loglar)
KVKK_PATTERNS=(
    "[0-9]{11}"
    "tc_kimlik"
    "tcno"
    "hasta_adi"
    "patient_name"
    "telefon.*05[0-9]{9}"
)

for pattern in "${KVKK_PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') KVKK_WARN: $FILE_PATH - $pattern" >> /tmp/norosera-kvkk-log.txt
    fi
done

exit 0
