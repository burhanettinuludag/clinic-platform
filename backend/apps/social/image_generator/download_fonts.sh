#!/bin/bash
# Download Inter fonts for social media image generator.
# Run: bash apps/social/image_generator/download_fonts.sh

FONT_DIR="$(dirname "$0")/fonts"
mkdir -p "$FONT_DIR"

echo "Downloading Inter fonts..."

# Inter font from Google Fonts
INTER_URL="https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"

cd "$FONT_DIR"

if command -v curl &> /dev/null; then
    curl -sL "$INTER_URL" -o inter.zip
elif command -v wget &> /dev/null; then
    wget -q "$INTER_URL" -O inter.zip
else
    echo "Error: curl or wget required"
    exit 1
fi

if [ -f inter.zip ]; then
    unzip -qo inter.zip "*.ttf" -d temp_inter 2>/dev/null || true

    # Find and copy the regular and bold variants
    find temp_inter -name "Inter-Regular.ttf" -exec cp {} ./Inter-Regular.ttf \; 2>/dev/null
    find temp_inter -name "Inter-Bold.ttf" -exec cp {} ./Inter-Bold.ttf \; 2>/dev/null

    # Fallback: try different naming
    if [ ! -f "Inter-Regular.ttf" ]; then
        find temp_inter -name "*Regular*" -name "*.ttf" | head -1 | xargs -I{} cp {} ./Inter-Regular.ttf 2>/dev/null
    fi
    if [ ! -f "Inter-Bold.ttf" ]; then
        find temp_inter -name "*Bold*" -name "*.ttf" | head -1 | xargs -I{} cp {} ./Inter-Bold.ttf 2>/dev/null
    fi

    rm -rf temp_inter inter.zip
    echo "Done! Fonts saved to $FONT_DIR"
    ls -la "$FONT_DIR"/*.ttf 2>/dev/null
else
    echo "Download failed"
    exit 1
fi
