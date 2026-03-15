#!/bin/bash
# Norosera — Masaustu bildirimi (Notification hook)

MESSAGE="${1:-Claude Code bildirim}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "display notification \"$MESSAGE\" with title \"Norosera - Claude Code\" sound name \"Glass\"" 2>/dev/null
elif command -v notify-send &>/dev/null; then
    notify-send "Norosera - Claude Code" "$MESSAGE" 2>/dev/null
fi

exit 0
