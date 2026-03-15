#!/bin/bash
# Norosera — Icerik uzunlugu kontrolu (Stop hook)
# Oturum sonunda olusturulan/degistirilen icerik dosyalarinin
# minimum karakter sinirini karsilayip karsilamadigini kontrol eder.

# Minimum karakter sinirlari
MIN_BLOG=3000
MIN_ARTICLE=5000
MIN_GUIDE=8000
MIN_CAPTION=500

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HAS_ERROR=0

# Session marker'dan beri degistirilen dosyalari bul
if [ -f /tmp/.norosera-session-marker ]; then
    MARKER_TIME=$(stat -f %m /tmp/.norosera-session-marker 2>/dev/null || stat -c %Y /tmp/.norosera-session-marker 2>/dev/null)
else
    exit 0
fi

# Sadece icerik dosyalarini kontrol et (backend content dizini + markdown)
CONTENT_FILES=$(find "$PROJECT_ROOT/backend/apps/content" -newer /tmp/.norosera-session-marker \
    -name "*.md" -o -name "*.txt" -o -name "*.html" 2>/dev/null | \
    grep -iE "(blog|makale|article|post|icerik|rehber|guide)" 2>/dev/null)

# Proje kokunde sadece icerikle ilgili markdown'lari kontrol et (README, CLAUDE.md vb. haric)
MD_FILES=$(find "$PROJECT_ROOT" -maxdepth 2 -newer /tmp/.norosera-session-marker \
    -name "*.md" 2>/dev/null | \
    grep -iE "(blog|makale|article|post|icerik|rehber|guide)" | \
    grep -viE "(README|CLAUDE|CHANGELOG|LICENSE|CONTRIBUTING|MEMORY|plan)" 2>/dev/null)

ALL_FILES="$CONTENT_FILES $MD_FILES"

for file in $ALL_FILES; do
    [ -z "$file" ] && continue
    [ ! -f "$file" ] && continue

    CHAR_COUNT=$(wc -m < "$file" | tr -d ' ')
    FILENAME=$(basename "$file")

    # Dosya tipine gore minimum belirle
    if echo "$FILENAME" | grep -qiE "(rehber|guide)"; then
        MIN=$MIN_GUIDE
        TYPE="Rehber"
    elif echo "$FILENAME" | grep -qiE "(makale|article)"; then
        MIN=$MIN_ARTICLE
        TYPE="Makale"
    elif echo "$FILENAME" | grep -qiE "(caption|social)"; then
        MIN=$MIN_CAPTION
        TYPE="Sosyal Medya"
    else
        MIN=$MIN_BLOG
        TYPE="Blog"
    fi

    if [ "$CHAR_COUNT" -lt "$MIN" ]; then
        DEFICIT=$((MIN - CHAR_COUNT))
        echo "UYARI: $TYPE icerigi cok kisa!"
        echo "  Dosya: $file"
        echo "  Mevcut: $CHAR_COUNT karakter | Minimum: $MIN karakter | Eksik: $DEFICIT karakter"
        echo "  Oneriler: Alt basliklar ekle, klinik ornekler ver, SSS bolumu ekle, tedavi detaylari yaz"
        echo ""
        HAS_ERROR=1
    fi
done

if [ $HAS_ERROR -eq 1 ]; then
    echo "Icerik uzunlugu yetersiz. Lutfen icerigi genisletin."
    exit 2
fi

exit 0
