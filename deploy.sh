#!/bin/bash
# ===========================================
# NOROSERA - Production Deployment Script
# ===========================================
# Usage: bash deploy.sh [init|update|ssl|restart]

set -e

PROJECT_DIR="/opt/norosera"
COMPOSE_FILE="docker-compose.prod.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

case "${1:-help}" in
  init)
    log "=== Initial deployment ==="

    # Use initial nginx (HTTP only) for first time
    log "Setting up initial nginx config (HTTP only)..."
    cp "$PROJECT_DIR/nginx/nginx.init.conf" "$PROJECT_DIR/nginx/active.conf"

    # Create log directory
    mkdir -p /var/log/clinic

    # Build images
    log "Building Docker images..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" build --no-cache

    # Start services
    log "Starting services..."
    docker compose -f "$COMPOSE_FILE" up -d

    # Wait for DB
    log "Waiting for database..."
    sleep 10

    # Run migrations
    log "Running Django migrations..."
    docker compose -f "$COMPOSE_FILE" exec backend python manage.py migrate --noinput

    # Collect static files
    log "Collecting static files..."
    docker compose -f "$COMPOSE_FILE" exec backend python manage.py collectstatic --noinput

    # Create superuser (interactive)
    log "Create admin superuser..."
    docker compose -f "$COMPOSE_FILE" exec backend python manage.py createsuperuser || true

    log "=== Initial deployment complete ==="
    log "Next step: Point DNS to this server, then run: bash deploy.sh ssl"
    ;;

  ssl)
    log "=== Setting up SSL certificates ==="

    DOMAIN="norosera.com"
    EMAIL="uludagburhan@yahoo.com"

    # Get SSL certificate
    log "Requesting SSL certificate for $DOMAIN..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" run --rm certbot certonly \
      --webroot \
      --webroot-path=/var/www/certbot \
      -d "$DOMAIN" \
      -d "www.$DOMAIN" \
      --email "$EMAIL" \
      --agree-tos \
      --no-eff-email

    # Switch to production nginx config (with SSL)
    log "Switching to SSL nginx config..."
    cp "$PROJECT_DIR/nginx/nginx.prod.conf" "$PROJECT_DIR/nginx/active.conf"

    # Reload nginx
    docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload

    # Set up auto-renewal cron
    log "Setting up SSL auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 3 * * * cd $PROJECT_DIR && docker compose -f $COMPOSE_FILE run --rm certbot renew --quiet && docker compose -f $COMPOSE_FILE exec nginx nginx -s reload") | crontab -

    log "=== SSL setup complete ==="
    log "Site is live at https://$DOMAIN"
    ;;

  update)
    log "=== Updating deployment ==="

    cd "$PROJECT_DIR"

    # Pull latest code (if using git)
    # git pull origin main

    # Rebuild and restart
    log "Rebuilding images..."
    docker compose -f "$COMPOSE_FILE" build

    log "Restarting services..."
    docker compose -f "$COMPOSE_FILE" up -d

    # Run migrations
    log "Running migrations..."
    docker compose -f "$COMPOSE_FILE" exec backend python manage.py migrate --noinput

    # Collect static
    log "Collecting static files..."
    docker compose -f "$COMPOSE_FILE" exec backend python manage.py collectstatic --noinput

    log "=== Update complete ==="
    ;;

  restart)
    log "=== Restarting services ==="
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" restart
    log "=== Restart complete ==="
    ;;

  logs)
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" logs -f --tail=100 ${2:-}
    ;;

  status)
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" ps
    ;;

  help|*)
    echo "Usage: bash deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  init      - First-time deployment (build, migrate, create admin)"
    echo "  ssl       - Set up SSL certificates (run after DNS is configured)"
    echo "  update    - Update deployment (rebuild, migrate)"
    echo "  restart   - Restart all services"
    echo "  logs      - View logs (optional: service name)"
    echo "  status    - Show service status"
    ;;
esac
