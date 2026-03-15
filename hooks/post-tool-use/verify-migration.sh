#!/bin/bash
# Norosera — Migration dogrulama (PostToolUse hook)
# makemigrations sonrasi migration dosyasinin olusturuldugunu dogrular.

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')

# Sadece makemigrations iceren komutlarda calis
if ! echo "$COMMAND" | grep -q "makemigrations"; then
    exit 0
fi

# stdout'u kontrol et
STDOUT=$(echo "$INPUT" | grep -o '"stdout"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"stdout"[[:space:]]*:[[:space:]]*"//;s/"$//')

if echo "$STDOUT" | grep -q "No changes detected"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') MIGRATION: Degisiklik yok" >> /tmp/norosera-hook-log.txt
elif echo "$STDOUT" | grep -q "Migrations for"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') MIGRATION: Yeni migration olusturuldu" >> /tmp/norosera-hook-log.txt
fi

exit 0
