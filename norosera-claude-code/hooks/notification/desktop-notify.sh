#!/bin/bash
# Notification hook: macOS desktop notification when Claude needs attention

INPUT=$(cat)
MESSAGE=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('message', 'Claude Code tamamlandı'))
" 2>/dev/null)

# macOS
if command -v osascript &> /dev/null; then
    osascript -e "display notification \"$MESSAGE\" with title \"🧠 Norosera - Claude Code\" sound name \"Glass\""
fi

# Linux
if command -v notify-send &> /dev/null; then
    notify-send "🧠 Norosera - Claude Code" "$MESSAGE"
fi

exit 0
