#!/bin/bash
# Stop hook: İçerik uzunluk kontrolü
# Son 10 dakikada oluşturulan/değiştirilen içerik dosyalarını kontrol eder
# Minimum karakter sayısının altındaysa Claude'u devam etmeye zorlar

MIN_BLOG=3000
MIN_ARTICLE=5000
MIN_GUIDE=8000
MIN_CAPTION=500
MIN_DEFAULT=3000

FAILED=0
REPORT=""

# Son 10 dakikada değişen markdown ve text dosyalarını bul
RECENT_FILES=$(find . -name "*.md" -o -name "*.txt" -o -name "*.html" \
    -newer /tmp/.norosera-session-marker 2>/dev/null | \
    grep -iE "(blog|makale|article|post|content|icerik|rehber|guide)" 2>/dev/null)

# Session marker yoksa oluştur (SessionStart hook'u da bunu yapabilir)
if [ ! -f /tmp/.norosera-session-marker ]; then
    touch /tmp/.norosera-session-marker
    exit 0
fi

for file in $RECENT_FILES; do
    if [ -f "$file" ]; then
        CHAR_COUNT=$(wc -m < "$file" | tr -d ' ')
        WORD_COUNT=$(wc -w < "$file" | tr -d ' ')
        FILENAME=$(basename "$file")

        # Dosya adına göre minimum belirle
        if echo "$FILENAME" | grep -qiE "(rehber|guide|kapsamli)"; then
            MINIMUM=$MIN_GUIDE
            TYPE="rehber"
        elif echo "$FILENAME" | grep -qiE "(makale|article|medikal)"; then
            MINIMUM=$MIN_ARTICLE
            TYPE="makale"
        elif echo "$FILENAME" | grep -qiE "(caption|sosyal|social|instagram|linkedin)"; then
            MINIMUM=$MIN_CAPTION
            TYPE="sosyal medya"
        else
            MINIMUM=$MIN_DEFAULT
            TYPE="blog"
        fi

        if [ "$CHAR_COUNT" -lt "$MINIMUM" ]; then
            FAILED=1
            DEFICIT=$((MINIMUM - CHAR_COUNT))
            REPORT="${REPORT}\n❌ ${file}: ${CHAR_COUNT} karakter (minimum: ${MINIMUM}, eksik: ${DEFICIT})"
            REPORT="${REPORT}\n   Tür: ${TYPE} | Kelime: ${WORD_COUNT}"
        fi
    fi
done

# Django blog draft modeli üzerinden de kontrol (eğer DB erişimi varsa)
DJANGO_CONTENT=$(find . -path "*/blog/content/*" -newer /tmp/.norosera-session-marker 2>/dev/null)
for file in $DJANGO_CONTENT; do
    if [ -f "$file" ]; then
        CHAR_COUNT=$(wc -m < "$file" | tr -d ' ')
        if [ "$CHAR_COUNT" -lt "$MIN_BLOG" ]; then
            FAILED=1
            DEFICIT=$((MIN_BLOG - CHAR_COUNT))
            REPORT="${REPORT}\n❌ ${file}: ${CHAR_COUNT} karakter (minimum: ${MIN_BLOG}, eksik: ${DEFICIT})"
        fi
    fi
done

if [ "$FAILED" -eq 1 ]; then
    echo -e "⚠️  İÇERİK UZUNLUK KONTROLÜ BAŞARISIZ\n${REPORT}" >&2
    echo ""
    echo '{"decision": "block", "reason": "İçerik minimum karakter sayısının altında. Lütfen içeriği genişletin: alt başlık ekleyin, klinik örnekler verin, SSS bölümü ekleyin. Detaylar stderr çıktısında."}' >&2
    exit 2
fi

exit 0
