#!/bin/bash

# --- Gemini Personality Master Setup ---
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}=== Initializing Gemini Personality & Architect ===${NC}"

# 1. Initialize Submodules
echo -e "
${BLUE}[*] Initializing Architect submodule...${NC}"
git submodule update --init --recursive

# 2. Run Architect Setup
if [ -f "architect/setup.sh" ]; then
    echo -e "${BLUE}[*] Running Architect framework setup...${NC}"
    cd architect
    chmod +x setup.sh
    ./setup.sh
    cd ..
fi

echo -e "
${GREEN}=== Master Setup Complete ===${NC}"
echo "Run 'source ~/.zshrc' to ensure aliases are active."
