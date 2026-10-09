# Git Flow Agent Guard (`git-flow-agent-guard`)

[![CI](https://github.com/<owner>/git-flow-agent-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/git-flow-agent-guard/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/<owner>/git-flow-agent-guard)](https://github.com/<owner>/git-flow-agent-guard/releases)

> A stack-agnostic AI agent skill for deterministic Git workflow enforcement, shift-left CI testing, dual-tier audit logging, and risk-managed auto-merging.

## Features

- **Branch Protection:** Strictly prohibits direct commits or pushes to `main` and `dev`.
- **Shift-Left CI:** Forces agents to run local linting, type-checking, testing, and building prior to PR creation.
- **Dual Audit Logging:** Automatically logs functional changes (`AGENT_CHANGELOG.md`) and working tree state with hard rollback commands (`AGENT_WORKING_TREE.log`).
- **Upstream Pull Reconciliation:** Analyzes incoming pull diffs and maps overlapping file collisions before rebasing/merging.
- **Risk Matrix Engine:** Evaluates change risk (1–5), blast radius, and revert costs to gate auto-merging into `dev`.

## Quick Start

### One-line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash
```

### Agent-Specific Install

```bash
# Cursor
curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash -s -- --agent cursor

# Windsurf
curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash -s -- --agent windsurf

# Claude Code
curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash -s -- --agent claude

# Generic / Other
curl -fsSL https://raw.githubusercontent.com/<owner>/git-flow-agent-guard/main/install.sh | bash -s -- --agent generic
```

### Manual Install

1. Copy `SKILL.md` into your agent skill directory:
   - **Cursor:** `.cursorrules`
   - **Windsurf:** `.windsurfrules`
   - **Claude Code:** `.claude/skills/git-flow-agent-guard.md`
   - **Aider/CLI:** Reference in your prompt

2. Copy `.agent-guard.json.template` to `.agent-guard.json` in your repository root.

3. Configure your stack-specific test/lint commands inside `.agent-guard.json`:

```json
{
  "verification": {
    "lint_command": "ruff check .",
    "typecheck_command": "mypy .",
    "test_command": "pytest",
    "build_command": "python -m py_compile $(find . -name '*.py')"
  }
}
```

## How It Works

### Agent Directive (`SKILL.md`)

The skill defines 5 core rules the agent must follow:

1. **Branching & Scope Isolation** — All work from `dev`, feature branches only
2. **Dual Audit Logging** — `AGENT_CHANGELOG.md` + `AGENT_WORKING_TREE.log` before every commit
3. **Upstream Pull Reconciliation** — Run `analyze-pull.py` before merge/rebase
4. **Local CI Pre-Flight** — Run verification commands, hard block on failure
5. **Dual-Tier Risk Review** — Run `evaluate-risk.py`, auto-merge gated by decision matrix

### Decision Matrix (Auto-Merge to `dev`)

| Dev Risk | Blast Radius | Revert Cost | Action |
|----------|--------------|-------------|--------|
| 1–3      | ANY          | ANY         | ✅ Auto-merge allowed |
| 4        | LOW          | LOW         | ✅ Auto-merge allowed |
| 4        | MEDIUM/HIGH  | ANY         | 👤 Human review required |
| 5        | ANY          | ANY         | 👤 Human review required |

> **`main` Direct Push Prohibition:** Merging into `main` requires human sign-off, passing remote CI, and promotion via Release Candidate (`release/vX.Y.Z`) or Feature Flags.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/analyze-pull.py` | Detects overlapping file conflicts with upstream before merge/rebase |
| `scripts/evaluate-risk.py` | Scores risk (1–5), blast radius, revert cost; gates auto-merge |
| `scripts/lib/guard.py` | Shared utilities (config, git, risk calc, verification) |

### Usage

```bash
# Check for upstream conflicts before pulling/merging
python scripts/analyze-pull.py --target dev

# Evaluate risk of current changes vs dev
python scripts/evaluate-risk.py --target dev

# Evaluate risk vs main (always blocks auto-merge)
python scripts/evaluate-risk.py --target main
```

Both scripts write detailed Markdown logs to `.agent-guard/logs/`:
- `LAST_PULL_ANALYSIS.md` — conflict analysis
- `LAST_RISK_EVALUATION.md` — risk scores, verification results, decision

## Configuration (`.agent-guard.json`)

```json
{
  "branches": {
    "main": "main",
    "dev": "dev",
    "release_prefix": "release/"
  },
  "verification": {
    "lint_command": "ruff check scripts/",
    "typecheck_command": "mypy scripts/lib/guard.py",
    "test_command": "pytest tests/ -v",
    "build_command": "python -m py_compile scripts/analyze-pull.py scripts/evaluate-risk.py scripts/lib/guard.py"
  },
  "risk": {
    "revert_cost_patterns": {
      "HIGH": ["migration", "schema", "*.sql", "*.prisma", "docker-compose*", ".github/workflows/*", "terraform/*", "package-lock.json", "yarn.lock", "Cargo.lock", "go.sum", "requirements.txt", "pyproject.toml"],
      "MEDIUM": ["config*", "settings*", "*.yaml", "*.yml", "*.toml", "*.ini", ".env*"]
    }
  }
}
```

### Revert Cost Patterns

The risk engine classifies changed files to determine revert cost:

- **HIGH:** Database migrations, schema changes, lockfiles, infrastructure, CI/CD configs
- **MEDIUM:** Configuration files, environment files
- **LOW:** Everything else (source code, tests, docs)

## Verified Agent Compatibility

| Agent | Install Method | Status |
|-------|---------------|--------|
| Cursor | `.cursorrules` append | ✅ Tested |
| Windsurf | `.windsurfrules` append | ✅ Tested |
| Claude Code | `.claude/skills/` | ✅ Tested |
| Aider | Prompt reference | ✅ Compatible |
| Generic CLI | Manual prompt | ✅ Compatible |

## Development

### Running Verification Locally

```bash
# Install dev dependencies
pip install ruff mypy pytest pytest-cov

# Run all checks
ruff check scripts/
mypy scripts/lib/guard.py
pytest tests/ -v
python -m py_compile scripts/analyze-pull.py scripts/evaluate-risk.py scripts/lib/guard.py

# Self-check
python scripts/evaluate-risk.py --target dev
python scripts/analyze-pull.py --target main
```

### Running Tests

```bash
pytest tests/ -v --cov=scripts/lib --cov-report=term-missing
```

## Releasing

```bash
# Create release branch
git checkout -b release/v0.1.0

# Tag and push
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will build and create a GitHub Release automatically.

## License

MIT — see [LICENSE](LICENSE) for details.

## Contributing

1. Fork and create a feature branch from `dev`
2. Make changes following the SKILL.md directives
3. Run `python scripts/evaluate-risk.py --target dev` — must pass
4. Open PR to `dev`

---

**Repository:** https://github.com/<owner>/git-flow-agent-guard