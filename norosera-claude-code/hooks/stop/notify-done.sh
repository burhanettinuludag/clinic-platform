#!/bin/bash
# Stop hook: Log session summary and notify

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log what changed
if command -v git &> /dev/null && [ -d ".git" ]; then
    CHANGED_FILES=$(git diff --name-only 2>/dev/null | wc -l)
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null | wc -l)
    echo "[$TIMESTAMP] Session ended. Changed: $CHANGED_FILES, Staged: $STAGED_FILES" >> /tmp/norosera-session-log.txt
fi

# macOS notification
if command -v osascript &> /dev/null; then
    osascript -e 'display notification "Claude Code oturumu tamamlandı ✅" with title "Norosera" sound name "Glass"'
fi

exit 0
