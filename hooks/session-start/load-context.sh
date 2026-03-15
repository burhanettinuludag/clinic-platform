#!/bin/bash
# Norosera — Oturum baslangic konteksti (SessionStart hook)
# Claude Code basladiginda proje durumunu yukler.

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Norosera Proje Durumu ==="
echo "Tarih: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Git durumu
if command -v git &>/dev/null && [ -d "$PROJECT_ROOT/.git" ]; then
    echo "--- Git ---"
    echo "Branch: $(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null)"
    CHANGES=$(git -C "$PROJECT_ROOT" status --porcelain 2>/dev/null | head -20)
    if [ -n "$CHANGES" ]; then
        CHANGE_COUNT=$(echo "$CHANGES" | wc -l | tr -d ' ')
        echo "Commit edilmemis degisiklik: $CHANGE_COUNT dosya"
    else
        echo "Calisan dizin temiz"
    fi
    echo ""
    echo "Son 5 commit:"
    git -C "$PROJECT_ROOT" log --oneline -5 2>/dev/null
    echo ""
fi

# Backend durumu
echo "--- Backend ---"
if [ -f "$PROJECT_ROOT/backend/.venv/bin/python3" ]; then
    PYTHON_VER=$("$PROJECT_ROOT/backend/.venv/bin/python3" --version 2>/dev/null)
    echo "Python: $PYTHON_VER"

    # Pending migration kontrolu
    cd "$PROJECT_ROOT/backend"
    PENDING=$(DJANGO_SETTINGS_MODULE=config.settings.development "$PROJECT_ROOT/backend/.venv/bin/python3" manage.py showmigrations --plan 2>/dev/null | grep '\[ \]' | wc -l | tr -d ' ')
    if [ "$PENDING" -gt 0 ]; then
        echo "Bekleyen migration: $PENDING"
    else
        echo "Tum migration'lar uygulandi"
    fi
else
    echo "Python venv bulunamadi (backend/.venv/)"
fi
echo ""

# Frontend durumu
echo "--- Frontend ---"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    NODE_VER=$(node --version 2>/dev/null)
    echo "Node.js: $NODE_VER"
    NEXT_VER=$(grep '"next"' "$PROJECT_ROOT/frontend/package.json" | head -1 | grep -o '[0-9][0-9.]*')
    echo "Next.js: $NEXT_VER"
fi
echo ""

# Docker durumu
echo "--- Docker ---"
if command -v docker &>/dev/null; then
    CONTAINERS=$(docker ps --format "{{.Names}}: {{.Status}}" 2>/dev/null)
    if [ -n "$CONTAINERS" ]; then
        echo "$CONTAINERS"
    else
        echo "Docker container calismyior"
    fi
else
    echo "Docker kurulu degil"
fi
echo ""

# Son uyarilar
if [ -f /tmp/norosera-hook-log.txt ]; then
    RECENT=$(tail -5 /tmp/norosera-hook-log.txt 2>/dev/null)
    if [ -n "$RECENT" ]; then
        echo "--- Son Hook Uyarilari ---"
        echo "$RECENT"
        echo ""
    fi
fi

if [ -f /tmp/norosera-kvkk-log.txt ]; then
    KVKK_COUNT=$(wc -l < /tmp/norosera-kvkk-log.txt 2>/dev/null | tr -d ' ')
    if [ "$KVKK_COUNT" -gt 0 ]; then
        echo "KVKK uyari sayisi: $KVKK_COUNT"
    fi
fi

# Session marker olustur (check-content-length icin)
touch /tmp/.norosera-session-marker
