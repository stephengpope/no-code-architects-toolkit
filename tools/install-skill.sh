#!/usr/bin/env bash
#
# Install the NCAToolkit Claude Skill
#
# This script:
#   1. Symlinks the skill into ~/.claude/skills/NCAToolkit/
#   2. Runs interactive setup to validate credentials and save to ~/.nca-toolkit/config
#
# Usage:
#   ./tools/install-skill.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_SOURCE="$SCRIPT_DIR/claude-skill"
SKILL_TARGET="$HOME/.claude/skills/NCAToolkit"
NCA_CLI="$PROJECT_DIR/tools/nca.py"

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

# ─── Step 2: Run setup (authenticate + save config) ──────────────────────────

echo -e "${YELLOW}Step 2:${RESET} Configuring API credentials"
echo ""

if [ -f "$HOME/.nca-toolkit/config" ]; then
    echo -e "  ${GREEN}Existing config found at ~/.nca-toolkit/config${RESET}"
    echo ""
    read -rp "  Re-run setup? [y/N]: " RERUN
    if [[ "$RERUN" =~ ^[Yy] ]]; then
        python3 "$NCA_CLI" connect
    else
        echo "  Keeping existing config."
    fi
else
    python3 "$NCA_CLI" connect
fi

echo ""

# ─── Step 3: Verify ──────────────────────────────────────────────────────────

echo -e "${YELLOW}Step 3:${RESET} Verifying installation"

if [ -L "$SKILL_TARGET" ] && [ -f "$SKILL_TARGET/SKILL.md" ]; then
    echo -e "  ${GREEN}Skill installed at $SKILL_TARGET${RESET}"
else
    echo -e "  ${YELLOW}Warning: Skill symlink may not be working correctly${RESET}"
fi

if [ -f "$NCA_CLI" ]; then
    echo -e "  ${GREEN}CLI tool found at $NCA_CLI${RESET}"
else
    echo -e "  ${YELLOW}Warning: CLI tool not found${RESET}"
fi

if [ -f "$HOME/.nca-toolkit/config" ]; then
    PERMS=$(stat -f "%Lp" "$HOME/.nca-toolkit/config" 2>/dev/null || stat -c "%a" "$HOME/.nca-toolkit/config" 2>/dev/null)
    echo -e "  ${GREEN}Config file at ~/.nca-toolkit/config (perms: $PERMS)${RESET}"
else
    echo -e "  ${YELLOW}Warning: Config file not found${RESET}"
fi

echo ""
echo -e "${GREEN}Installation complete!${RESET}"
echo ""
echo -e "  ${BLUE}Test it:${RESET}"
echo -e "  ${CYAN}python3 $NCA_CLI test${RESET}"
echo ""
echo -e "  ${BLUE}Show config:${RESET}"
echo -e "  ${CYAN}python3 $NCA_CLI config${RESET}"
echo ""
echo -e "  ${BLUE}Use in Claude:${RESET}"
echo -e "  ${CYAN}\"Transcribe this video: https://example.com/video.mp4\"${RESET}"
echo ""
