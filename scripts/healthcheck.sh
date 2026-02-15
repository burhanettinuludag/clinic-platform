#!/bin/bash
# ===========================================
# NOROSERA - Uptime Health Check
# ===========================================
# Kullanim: ./scripts/healthcheck.sh
# Cron: */5 * * * * /opt/norosera/scripts/healthcheck.sh

URL="https://norosera.com/api/v1/health/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 $URL)

if [ "$RESPONSE" != "200" ]; then
    echo "$(date): ALERT - Site down! HTTP $RESPONSE" >> /var/log/clinic/uptime.log
    # Opsiyonel: email uyarisi
    # echo "Norosera DOWN - HTTP $RESPONSE" | mail -s "ALERT: Norosera Down" admin@norosera.com
    # Opsiyonel: Telegram uyarisi
    # curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    #   -d chat_id="${TELEGRAM_CHAT_ID}" -d text="ALERT: Norosera DOWN - HTTP $RESPONSE"
fi
