#!/bin/bash
# Script to update translation files for Samba Configurator

# Configuration
TRANSLATOR_NAME="Samuele Gallicani"
TRANSLATOR_EMAIL="samu.gallicani@gmail.com"
PROJECT_NAME="Samba Configurator"
PROJECT_VERSION="1.0.0"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Updating translations for ${PROJECT_NAME}...${NC}"

# Extract translatable strings from Python files
echo -e "${GREEN}1. Extracting strings...${NC}"
xgettext --language=Python --keyword=_ --output=po/samba-configurator.pot \
    --package-name="${PROJECT_NAME}" \
    --package-version="${PROJECT_VERSION}" \
    --msgid-bugs-address="${TRANSLATOR_EMAIL}" \
    --copyright-holder="${TRANSLATOR_NAME}" \
    *.py

# Update existing .po files
echo -e "${GREEN}2. Updating .po files...${NC}"
for po_file in po/*.po; do
    if [ -f "$po_file" ]; then
        echo "   Updating $po_file"
        msgmerge --update "$po_file" po/samba-configurator.pot
    fi
done

# Compile .po files to .mo files
echo -e "${GREEN}3. Compiling translations...${NC}"
for po_file in po/*.po; do
    if [ -f "$po_file" ]; then
        # Extract language code from filename (e.g., it.po -> it)
        lang=$(basename "$po_file" .po)
        
        # Create locale directory if it doesn't exist
        mkdir -p "locale/${lang}/LC_MESSAGES"
        
        # Compile .po to .mo
        echo "   Compiling $po_file -> locale/${lang}/LC_MESSAGES/samba-configurator.mo"
        msgfmt "$po_file" -o "locale/${lang}/LC_MESSAGES/samba-configurator.mo"
    fi
done

echo -e "${BLUE}Translation update complete!${NC}"
echo ""
echo "To add a new language, run:"
echo "  msginit --input=po/samba-configurator.pot --locale=LANG --output=po/LANG.po"
echo "  (Replace LANG with language code, e.g., es, fr, de)"
