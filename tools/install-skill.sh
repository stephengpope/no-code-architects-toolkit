#!/usr/bin/env bash
#
# Install the NCAToolkit Claude Skill
#
# This script:
#   1. Symlinks the skill into ~/.claude/skills/NCAToolkit/
#   2. Prompts for NCA_API_URL and NCA_API_KEY if not already set
#   3. Adds env vars to your shell profile
#
# Usage:
#   ./tools/install-skill.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_SOURCE="$SCRIPT_DIR/claude-skill"
SKILL_TARGET="$HOME/.claude/skills/NCAToolkit"

# Colors
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║${RESET}  ${GREEN}NCA Toolkit - Claude Skill Installer${RESET}       ${BLUE}║${RESET}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ─── Step 1: Create symlink ──────────────────────────────────────────────────

echo -e "${YELLOW}Step 1:${RESET} Installing skill to ${CYAN}$SKILL_TARGET${RESET}"

if [ -L "$SKILL_TARGET" ]; then
    echo "  Removing existing symlink..."
    rm "$SKILL_TARGET"
elif [ -d "$SKILL_TARGET" ]; then
    echo "  Backing up existing directory to ${SKILL_TARGET}.bak..."
    mv "$SKILL_TARGET" "${SKILL_TARGET}.bak"
fi

mkdir -p "$HOME/.claude/skills"
ln -s "$SKILL_SOURCE" "$SKILL_TARGET"
echo -e "  ${GREEN}Skill symlinked successfully${RESET}"
echo ""

# ─── Step 2: Configure environment variables ─────────────────────────────────

echo -e "${YELLOW}Step 2:${RESET} Configuring environment variables"
echo ""

# Detect shell profile
if [ -n "${ZSH_VERSION:-}" ] || [ "$SHELL" = */zsh ]; then
    PROFILE="$HOME/.zshrc"
else
    PROFILE="$HOME/.bashrc"
fi

NEEDS_VARS=false

if [ -z "${NCA_API_URL:-}" ]; then
    echo -e "  ${CYAN}NCA_API_URL${RESET} is not set."
    read -rp "  Enter your NCA Toolkit API URL: " NCA_API_URL
    if [ -n "$NCA_API_URL" ]; then
        echo "" >> "$PROFILE"
        echo "# NCA Toolkit API" >> "$PROFILE"
        echo "export NCA_API_URL=\"$NCA_API_URL\"" >> "$PROFILE"
        NEEDS_VARS=true
        echo -e "  ${GREEN}Added to $PROFILE${RESET}"
    fi
else
    echo -e "  ${GREEN}NCA_API_URL${RESET} = ${CYAN}${NCA_API_URL}${RESET}"
fi

if [ -z "${NCA_API_KEY:-}" ]; then
    echo -e "  ${CYAN}NCA_API_KEY${RESET} is not set."
    read -rp "  Enter your NCA Toolkit API key: " NCA_API_KEY
    if [ -n "$NCA_API_KEY" ]; then
        # Only add header comment if we didn't just add it
        if [ "$NEEDS_VARS" = false ]; then
            echo "" >> "$PROFILE"
            echo "# NCA Toolkit API" >> "$PROFILE"
        fi
        echo "export NCA_API_KEY=\"$NCA_API_KEY\"" >> "$PROFILE"
        NEEDS_VARS=true
        echo -e "  ${GREEN}Added to $PROFILE${RESET}"
    fi
else
    echo -e "  ${GREEN}NCA_API_KEY${RESET} = ${CYAN}(set)${RESET}"
fi

echo ""

# ─── Step 3: Verify ──────────────────────────────────────────────────────────

echo -e "${YELLOW}Step 3:${RESET} Verifying installation"

if [ -L "$SKILL_TARGET" ] && [ -f "$SKILL_TARGET/SKILL.md" ]; then
    echo -e "  ${GREEN}Skill installed at $SKILL_TARGET${RESET}"
else
    echo -e "  ${YELLOW}Warning: Skill symlink may not be working correctly${RESET}"
fi

if [ -f "$PROJECT_DIR/tools/nca.py" ]; then
    echo -e "  ${GREEN}CLI tool found at $PROJECT_DIR/tools/nca.py${RESET}"
else
    echo -e "  ${YELLOW}Warning: CLI tool not found${RESET}"
fi

echo ""
echo -e "${GREEN}Installation complete!${RESET}"
echo ""

if [ "$NEEDS_VARS" = true ]; then
    echo -e "  ${YELLOW}Run this to load the new env vars:${RESET}"
    echo -e "  ${CYAN}source $PROFILE${RESET}"
    echo ""
fi

echo -e "  ${BLUE}Test it:${RESET}"
echo -e "  ${CYAN}python $PROJECT_DIR/tools/nca.py test${RESET}"
echo ""
echo -e "  ${BLUE}Use in Claude:${RESET}"
echo -e "  ${CYAN}\"Transcribe this video: https://example.com/video.mp4\"${RESET}"
echo ""
