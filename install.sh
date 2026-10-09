#!/usr/bin/env bash
# git-flow-agent-guard installer
# Usage: curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash
# Or: ./install.sh [--target-dir DIR] [--agent AGENT]

set -euo pipefail

REPO_URL="https://github.com/MessilineHani/git-flow-agent-guard"
RAW_BASE="https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main"
TARGET_DIR="."
AGENT=""

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Installs git-flow-agent-guard into your project.

Options:
    --target-dir DIR    Target directory (default: current directory)
    --agent AGENT       Agent type: cursor, windsurf, claude, aider, generic (default: generic)
    --help              Show this help

Examples:
    $0                          # Install to current dir
    $0 --agent cursor           # Install and append to .cursorrules
    $0 --target-dir ../my-proj  # Install to another project
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --target-dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        --agent)
            AGENT="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
echo "Installing to: $TARGET_DIR"

# Files to copy
FILES=(
    "SKILL.md"
    "scripts/analyze-pull.py"
    "scripts/evaluate-risk.py"
    "scripts/lib/guard.py"
    ".agent-guard.json.template"
)

# Create target structure
mkdir -p "$TARGET_DIR/.agent-guard/logs"
mkdir -p "$TARGET_DIR/scripts/lib"

# Copy files
for file in "${FILES[@]}"; do
    dest="$TARGET_DIR/$file"
    mkdir -p "$(dirname "$dest")"
    curl -fsSL "$RAW_BASE/$file" -o "$dest"
    echo "  ✓ $file"
done

# Copy .agent-guard.json if not exists
if [[ ! -f "$TARGET_DIR/.agent-guard.json" ]]; then
    curl -fsSL "$RAW_BASE/.agent-guard.json.template" -o "$TARGET_DIR/.agent-guard.json"
    echo "  ✓ .agent-guard.json (from template)"
else
    echo "  ⊘ .agent-guard.json (already exists, skipping)"
fi

# Make scripts executable
chmod +x "$TARGET_DIR/scripts/analyze-pull.py"
chmod +x "$TARGET_DIR/scripts/evaluate-risk.py"

# Agent-specific setup
case "$AGENT" in
    cursor)
        if [[ -f "$TARGET_DIR/.cursorrules" ]]; then
            echo "" >> "$TARGET_DIR/.cursorrules"
            echo "---" >> "$TARGET_DIR/.cursorrules"
            cat "$TARGET_DIR/SKILL.md" >> "$TARGET_DIR/.cursorrules"
            echo "  ✓ Appended SKILL.md to .cursorrules"
        else
            cp "$TARGET_DIR/SKILL.md" "$TARGET_DIR/.cursorrules"
            echo "  ✓ Created .cursorrules from SKILL.md"
        fi
        ;;
    windsurf)
        if [[ -f "$TARGET_DIR/.windsurfrules" ]]; then
            echo "" >> "$TARGET_DIR/.windsurfrules"
            echo "---" >> "$TARGET_DIR/.windsurfrules"
            cat "$TARGET_DIR/SKILL.md" >> "$TARGET_DIR/.windsurfrules"
            echo "  ✓ Appended SKILL.md to .windsurfrules"
        else
            cp "$TARGET_DIR/SKILL.md" "$TARGET_DIR/.windsurfrules"
            echo "  ✓ Created .windsurfrules from SKILL.md"
        fi
        ;;
    claude)
        mkdir -p "$TARGET_DIR/.claude/skills"
        cp "$TARGET_DIR/SKILL.md" "$TARGET_DIR/.claude/skills/git-flow-agent-guard.md"
        echo "  ✓ Installed to .claude/skills/"
        ;;
    aider)
        echo "For Aider, add to your prompt: 'Read SKILL.md and strictly follow its directives for all git operations.'"
        ;;
    generic|"")
        echo "  ✓ Generic install complete. Read SKILL.md and follow its directives."
        ;;
    *)
        echo "Warning: Unknown agent '$AGENT', using generic install" >&2
        ;;
esac

cat <<EOF

✅ Installation complete!

Next steps:
1. Review and customize .agent-guard.json for your stack
2. Run verification: python scripts/evaluate-risk.py --target dev
3. Read SKILL.md for the full agent directive

Repository: $REPO_URL
EOF