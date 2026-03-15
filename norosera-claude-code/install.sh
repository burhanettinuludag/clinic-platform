#!/bin/bash
# ============================================================
# Norosera Claude Code Otomasyon Paketi — Kurulum Scripti
# ============================================================
# Kullanım: bash install.sh /path/to/clinic-platform
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🧠 Norosera — Claude Code Otomasyon Paketi    ║${NC}"
echo -e "${BLUE}║   Hooks • Skills • Agents • Commands             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Target directory
TARGET="${1:-.}"

if [ ! -d "$TARGET" ]; then
    echo -e "${RED}❌ Hata: '$TARGET' dizini bulunamadı.${NC}"
    echo "Kullanım: bash install.sh /path/to/clinic-platform"
    exit 1
fi

# Resolve absolute path
TARGET=$(cd "$TARGET" && pwd)
echo -e "${YELLOW}📁 Hedef dizin: $TARGET${NC}"

# Verify it looks like the Norosera project
if [ ! -f "$TARGET/backend/manage.py" ] && [ ! -f "$TARGET/frontend/package.json" ]; then
    echo -e "${YELLOW}⚠️  Uyarı: Bu dizin Norosera projesine benzemiyor.${NC}"
    read -p "Yine de devam etmek istiyor musunuz? (e/h): " CONFIRM
    if [ "$CONFIRM" != "e" ]; then
        echo "İptal edildi."
        exit 0
    fi
fi

# Backup existing config
if [ -f "$TARGET/CLAUDE.md" ]; then
    echo -e "${YELLOW}📋 Mevcut CLAUDE.md yedekleniyor → CLAUDE.md.backup${NC}"
    cp "$TARGET/CLAUDE.md" "$TARGET/CLAUDE.md.backup"
fi

if [ -d "$TARGET/.claude" ]; then
    echo -e "${YELLOW}📋 Mevcut .claude/ yedekleniyor → .claude.backup/${NC}"
    cp -r "$TARGET/.claude" "$TARGET/.claude.backup"
fi

# Create directory structure
echo -e "${GREEN}📂 Dizin yapısı oluşturuluyor...${NC}"
mkdir -p "$TARGET/.claude/commands"
mkdir -p "$TARGET/.claude/skills"
mkdir -p "$TARGET/hooks/pre-tool-use"
mkdir -p "$TARGET/hooks/post-tool-use"
mkdir -p "$TARGET/hooks/stop"
mkdir -p "$TARGET/hooks/session-start"
mkdir -p "$TARGET/hooks/notification"

# Get script directory (where the package files are)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy CLAUDE.md
echo -e "${GREEN}📝 CLAUDE.md kopyalanıyor...${NC}"
cp "$SCRIPT_DIR/CLAUDE.md" "$TARGET/CLAUDE.md"

# Copy settings.json
echo -e "${GREEN}⚙️  Hook ayarları kopyalanıyor...${NC}"
cp "$SCRIPT_DIR/.claude/settings.json" "$TARGET/.claude/settings.json"

# Copy skills
echo -e "${GREEN}🎯 Skills kopyalanıyor...${NC}"
SKILL_COUNT=0
for skill in "$SCRIPT_DIR/.claude/skills/"*.md; do
    if [ -f "$skill" ]; then
        cp "$skill" "$TARGET/.claude/skills/"
        SKILL_COUNT=$((SKILL_COUNT + 1))
        echo "   ✓ $(basename "$skill")"
    fi
done

# Copy commands
echo -e "${GREEN}⌨️  Slash commands kopyalanıyor...${NC}"
CMD_COUNT=0
for cmd in "$SCRIPT_DIR/.claude/commands/"*.md; do
    if [ -f "$cmd" ]; then
        cp "$cmd" "$TARGET/.claude/commands/"
        CMD_COUNT=$((CMD_COUNT + 1))
        echo "   ✓ /$(basename "$cmd" .md)"
    fi
done

# Copy hooks
echo -e "${GREEN}🪝 Hooks kopyalanıyor...${NC}"
HOOK_COUNT=0
for hook_dir in pre-tool-use post-tool-use stop session-start notification; do
    for hook in "$SCRIPT_DIR/hooks/$hook_dir/"*.sh; do
        if [ -f "$hook" ]; then
            cp "$hook" "$TARGET/hooks/$hook_dir/"
            chmod +x "$TARGET/hooks/$hook_dir/$(basename "$hook")"
            HOOK_COUNT=$((HOOK_COUNT + 1))
            echo "   ✓ $hook_dir/$(basename "$hook")"
        fi
    done
done

# Make all hooks executable
find "$TARGET/hooks" -name "*.sh" -exec chmod +x {} \;

# Add hooks directory to .gitignore if not already there
if [ -f "$TARGET/.gitignore" ]; then
    if ! grep -q "norosera-hook-log" "$TARGET/.gitignore"; then
        echo "" >> "$TARGET/.gitignore"
        echo "# Claude Code hook logs" >> "$TARGET/.gitignore"
        echo "/tmp/norosera-*.txt" >> "$TARGET/.gitignore"
    fi
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ KURULUM TAMAMLANDI               ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  📝 CLAUDE.md          → Proje kuralları         ║${NC}"
echo -e "${GREEN}║  🎯 $SKILL_COUNT Skills              → Otomatik yetenek      ║${NC}"
echo -e "${GREEN}║  ⌨️  $CMD_COUNT Commands            → /test /review /deploy  ║${NC}"
echo -e "${GREEN}║  🪝 $HOOK_COUNT Hooks               → Güvenlik & otomasyon  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Kullanım:${NC}"
echo "  cd $TARGET"
echo "  claude                          # Claude Code başlat"
echo "  /test                           # Tüm testleri çalıştır"
echo "  /review                         # Kod inceleme"
echo "  /deploy                         # Deploy hazırlığı"
echo "  /commit                         # Akıllı commit"
echo "  /doc                            # Dokümantasyon oluştur"
echo "  /newapp <isim>                  # Yeni Django app"
echo "  /security                       # Güvenlik taraması"
echo ""
echo -e "${YELLOW}💡 İpucu: Claude Code terminalinde herhangi bir şey yazın,${NC}"
echo -e "${YELLOW}   ilgili skill'ler otomatik devreye girecektir.${NC}"
echo ""
