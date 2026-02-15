#!/bin/bash
# ============================================
# Norosera - Guvenli secret uretici
# ============================================
# Kullanim: ./scripts/generate_secrets.sh

echo "=== Norosera Production Secrets ==="
echo ""
echo "DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
echo "DB_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+')"
echo ""
echo "Bu degerleri .env dosyaniza yapistirin."
