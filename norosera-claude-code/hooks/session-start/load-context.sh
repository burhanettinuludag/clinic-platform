#!/bin/bash
# SessionStart hook: Load project context into Claude's awareness
# stdout from this hook becomes part of Claude's context

echo "=== NOROSERA SESSION CONTEXT ==="
echo "Tarih: $(date '+%Y-%m-%d %H:%M')"
echo ""

# Session marker for content length tracking
touch /tmp/.norosera-session-marker

# Git status
if command -v git &> /dev/null && [ -d ".git" ]; then
    echo "📌 Git Branch: $(git branch --show-current 2>/dev/null)"
    echo "📊 Uncommitted changes:"
    git status --short 2>/dev/null | head -20
    echo ""
    echo "📝 Son 5 commit:"
    git log --oneline -5 2>/dev/null
    echo ""
fi

# Check backend health
if [ -f "backend/manage.py" ]; then
    echo "🐍 Backend Status:"
    echo "  - Python: $(python3 --version 2>/dev/null)"
    echo "  - Pending migrations: $(cd backend && python3 manage.py showmigrations --plan 2>/dev/null | grep '\[ \]' | wc -l) adet"
    echo ""
fi

# Check frontend health
if [ -f "frontend/package.json" ]; then
    echo "⚛️  Frontend Status:"
    echo "  - Node: $(node --version 2>/dev/null)"
    echo "  - Next.js: $(cd frontend && node -e "console.log(require('./package.json').dependencies.next)" 2>/dev/null)"
    echo ""
fi

# Docker status
if command -v docker &> /dev/null; then
    RUNNING=$(docker ps --format '{{.Names}}' 2>/dev/null | tr '\n' ', ')
    echo "🐳 Docker containers: ${RUNNING:-none}"
    echo ""
fi

# Recent hook warnings
if [ -f "/tmp/norosera-hook-log.txt" ]; then
    RECENT=$(tail -5 /tmp/norosera-hook-log.txt 2>/dev/null)
    if [ -n "$RECENT" ]; then
        echo "⚠️  Son hook uyarıları:"
        echo "$RECENT"
        echo ""
    fi
fi

# KVKK warnings
if [ -f "/tmp/norosera-kvkk-log.txt" ]; then
    KVKK_COUNT=$(wc -l < /tmp/norosera-kvkk-log.txt 2>/dev/null)
    if [ "$KVKK_COUNT" -gt 0 ]; then
        echo "🔒 KVKK Uyarı sayısı: $KVKK_COUNT (detay: /tmp/norosera-kvkk-log.txt)"
    fi
fi

echo "=== SESSION BAŞLADI ==="
