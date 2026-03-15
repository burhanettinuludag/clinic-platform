#!/bin/bash
# Norosera — Oturum tamamlandi bildirimi (Stop hook)

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Oturum ozeti logla
CHANGED=$(git -C "$PROJECT_ROOT" diff --stat 2>/dev/null | tail -1)
STAGED=$(git -C "$PROJECT_ROOT" diff --cached --stat 2>/dev/null | tail -1)

echo "$(date '+%Y-%m-%d %H:%M:%S') SESSION_END: changed=[$CHANGED] staged=[$STAGED]" >> /tmp/norosera-session-log.txt

# macOS bildirimi
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'display notification "Claude Code oturumu tamamlandi" with title "Norosera" sound name "Glass"' 2>/dev/null
elif command -v notify-send &>/dev/null; then
    notify-send "Norosera" "Claude Code oturumu tamamlandi" 2>/dev/null
fi

exit 0
