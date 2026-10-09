# Git Flow Agent Guard (`git-flow-agent-guard`)

> A stack-agnostic AI agent skill for deterministic Git workflow enforcement, shift-left CI testing, dual-tier audit logging, and risk-managed auto-merging.

## Features

- **Branch Protection:** Strictly prohibits direct commits or pushes to `main` and `dev`.
- **Shift-Left CI:** Forces agents to run local linting, type-checking, testing, and building prior to PR creation.
- **Dual Audit Logging:** Automatically logs functional changes (`AGENT_CHANGELOG.md`) and working tree state with hard rollback commands (`AGENT_WORKING_TREE.log`).
- **Upstream Pull Reconciliation:** Analyzes incoming pull diffs and maps overlapping file collisions before rebasing/merging.
- **Risk Matrix Engine:** Evaluates change risk (1–5), blast radius, and revert costs to gate auto-merging into `dev`.

## Quick Start

1. Copy `SKILL.md` into your agent skill directory (e.g., `.claude/skills/`, `.cursor/rules/`, or your custom agent folder).
2. Copy `.agent-guard.json.template` to `.agent-guard.json` in your repository root.
3. Configure your stack-specific test/lint commands inside `.agent-guard.json`.

```json
{
  "verification": {
    "lint_command": "cargo clippy",
    "typecheck_command": "cargo check",
    "test_command": "cargo test",
    "build_command": "cargo build --release"
  }
}

## How to Install & Use

Because different AI agents handle context differently, installation depends on your tool:

**For Cursor / Windsurf:**
Copy the contents of `SKILL.md` and paste them at the top of your `.cursorrules` or `.windsurfrules` file.

**For CLI Agents (Claude Code, Aider, etc.):**
1. Clone this repository into your project root or a `.agents/` folder.
2. Prompt your agent: `Read git-flow-agent-guard/SKILL.md and strictly follow its directives for all git operations.`

**For Web LLMs (Gemini, ChatGPT Plus, Claude 3.5):**
Provide the link to this repository and prompt: `Review the git-flow-agent-guard repository. Act as my coding assistant and strictly enforce these workflow, branching, and logging rules.`