# Git Flow Agent Guard (`git-flow-agent-guard`)

[![CI](https://github.com/MessilineHani/git-flow-agent-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/MessilineHani/git-flow-agent-guard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/MessilineHani/git-flow-agent-guard)](https://github.com/MessilineHani/git-flow-agent-guard/releases)

> **Stack-agnostic** AI agent skill for deterministic Git workflow enforcement, shift-left CI testing, dual-tier audit logging, and risk-managed auto-merging.

## What "Stack-Agnostic" Means Here

| Layer | Technology | Stack Dependency |
|-------|------------|------------------|
| **Evaluation Engine** | Python 3.8+ | Required only to run the guard scripts |
| **Your Project** | **Any** (Rust, Go, Node, Python, Java, .NET, etc.) | **Zero** — configure your own commands |
| **Risk Patterns** | Config-driven | Pre-loaded with 30+ patterns across 10+ ecosystems |
| **Agent Integration** | Prompt/Rule files | Works with any AI agent (Cursor, Windsurf, Claude, Aider, etc.) |

**The guard scripts analyze YOUR repository using YOUR configured commands.** They don't assume Python, don't parse your source code, and don't require any project-specific structure.

---

## Features

- **Branch Protection:** Strictly prohibits direct commits or pushes to `main` and `dev`.
- **Shift-Left CI:** Forces agents to run **your** local linting, type-checking, testing, and building prior to PR creation.
- **Dual Audit Logging:** Automatically logs functional changes (`AGENT_CHANGELOG.md`) and working tree state with hard rollback commands (`AGENT_WORKING_TREE.log`).
- **Upstream Pull Reconciliation:** Analyzes incoming pull diffs and maps overlapping file collisions before rebasing/merging.
- **Risk Matrix Engine:** Evaluates change risk (1–5), blast radius, and revert costs to gate auto-merging into `dev`.

---

## Quick Start

### For Non-Technical Users (Recommended) — Zero Config

Run the **bootstrap skill** once — it asks your stack, installs everything, and configures your commands:

```bash
# 1. Install bootstrap skill (one-time)
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/SKILL.bootstrap.md -o .cursorrules  # or .windsurfrules, .claude/skills/bootstrap.md

# 2. Tell your agent: "Run the git-flow-agent-guard-bootstrap skill"
#    → It will ask your stack, run installer, write YOUR commands to .agent-guard.json

# 3. After bootstrap says "done", replace bootstrap skill with main skill:
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/SKILL.md -o .cursorrules  # or your agent's config
```

> The bootstrap skill (`SKILL.bootstrap.md`) is a one-time setup wizard. Discard it after use.

### Manual Install (Developers)

```bash
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/install.sh | bash
```

### Agent-Specific Install

```bash
# Cursor
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/install.sh | bash -s -- --agent cursor

# Windsurf
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/install.sh | bash -s -- --agent windsurf

# Claude Code
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/install.sh | bash -s -- --agent claude

# Generic / Other
curl -fsSL https://raw.githubusercontent.com/MessilineHani/git-flow-agent-guard/main/install.sh | bash -s -- --agent generic
```

### Manual Install

1. Copy `SKILL.md` into your agent skill directory:
   - **Cursor:** `.cursorrules`
   - **Windsurf:** `.windsurfrules`
   - **Claude Code:** `.claude/skills/git-flow-agent-guard.md`
   - **Aider/CLI:** Reference in your prompt

2. Copy `.agent-guard.json.template` to `.agent-guard.json` in your repository root.

3. **Configure YOUR stack-specific commands** inside `.agent-guard.json`:

---

## Stack-Specific Configuration Examples

### Rust
```json
{
  "verification": {
    "lint_command": "cargo clippy -- -D warnings",
    "typecheck_command": "cargo check",
    "test_command": "cargo test",
    "build_command": "cargo build --release"
  }
}
```

### Go
```json
{
  "verification": {
    "lint_command": "golangci-lint run",
    "typecheck_command": "go vet ./...",
    "test_command": "go test ./...",
    "build_command": "go build ./..."
  }
}
```

### Node.js / TypeScript
```json
{
  "verification": {
    "lint_command": "eslint . --ext .ts,.js",
    "typecheck_command": "tsc --noEmit",
    "test_command": "vitest run",
    "build_command": "tsc && tsc-alias"
  }
}
```

### Python
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

### Java (Maven)
```json
{
  "verification": {
    "lint_command": "mvn checkstyle:check",
    "typecheck_command": "mvn compile",
    "test_command": "mvn test",
    "build_command": "mvn package -DskipTests"
  }
}
```

### .NET
```json
{
  "verification": {
    "lint_command": "dotnet format --verify-no-changes",
    "typecheck_command": "dotnet build --no-restore",
    "test_command": "dotnet test --no-build",
    "build_command": "dotnet publish -c Release"
  }
}
```

### Multi-Language / Monorepo
```json
{
  "verification": {
    "lint_command": "turbo run lint",
    "typecheck_command": "turbo run typecheck",
    "test_command": "turbo run test",
    "build_command": "turbo run build"
  }
}
```

> **Tip:** Empty commands (`""`) are skipped. Start with one command and add more as needed.

---

## How It Works

### Agent Directive (`SKILL.md`)

The skill defines 5 core rules the agent must follow:

1. **Branching & Scope Isolation** — All work from `dev`, feature branches only (`feat/`, `fix/`, `chore/`, etc.)
2. **Dual Audit Logging** — `AGENT_CHANGELOG.md` + `AGENT_WORKING_TREE.log` before every commit
3. **Upstream Pull Reconciliation** — Run `analyze-pull.py` before merge/rebase
4. **Local CI Pre-Flight** — Run **your configured** verification commands, hard block on failure
5. **Dual-Tier Risk Review** — Run `evaluate-risk.py`, auto-merge gated by decision matrix

### Decision Matrix (Auto-Merge to `dev`)

| Dev Risk | Blast Radius | Revert Cost | Action |
|----------|--------------|-------------|--------|
| 1–3      | ANY          | ANY         | ✅ Auto-merge allowed |
| 4        | LOW          | LOW         | ✅ Auto-merge allowed |
| 4        | MEDIUM/HIGH  | ANY         | 👤 Human review required |
| 5        | ANY          | ANY         | 👤 Human review required |

> **`main` Direct Push Prohibition:** Merging into `main` requires human sign-off, passing remote CI, and promotion via Release Candidate (`release/vX.Y.Z`) or Feature Flags.

---

## Scripts

| Script | Purpose | Stack Dependency |
|--------|---------|------------------|
| `scripts/analyze-pull.py` | Detects overlapping file conflicts with upstream before merge/rebase | **None** — pure Git |
| `scripts/evaluate-risk.py` | Scores risk (1–5), blast radius, revert cost; gates auto-merge | **None** — uses your config |
| `scripts/lib/guard.py` | Shared utilities (config, git, risk calc, verification) | **None** — pure Python stdlib |

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

---

## Configuration (`.agent-guard.json`)

```json
{
  "branches": {
    "main": "main",
    "dev": "dev",
    "release_prefix": "release/"
  },
  "verification": {
    "lint_command": "",
    "typecheck_command": "",
    "test_command": "",
    "build_command": ""
  },
  "risk": {
    "revert_cost_patterns": {
      "HIGH": [
        "migration", "schema", "*.sql", "*.prisma", "*.proto",
        "docker-compose*", ".github/workflows/*", "terraform/*",
        "kubernetes/*", "helm/*", "package-lock.json", "yarn.lock",
        "pnpm-lock.yaml", "Cargo.lock", "go.sum", "go.mod",
        "requirements.txt", "pyproject.toml", "Pipfile.lock",
        "poetry.lock", "pom.xml", "build.gradle*", "*.csproj",
        "composer.lock", "Gemfile.lock", "mix.lock", "rebar.lock"
      ],
      "MEDIUM": [
        "config*", "settings*", "*.yaml", "*.yml", "*.toml",
        "*.ini", ".env*", "Dockerfile*", "dockerignore",
        ".gitignore", ".editorconfig", "Makefile*", "*.mk"
      ]
    }
  }
}
```

### Revert Cost Patterns (Pre-loaded, Extensible)

The risk engine classifies changed files to determine revert cost. Patterns cover:

| Ecosystem | HIGH Patterns | MEDIUM Patterns |
|-----------|---------------|-----------------|
| **Database** | `migration`, `schema`, `*.sql`, `*.prisma` | — |
| **Infrastructure** | `terraform/*`, `kubernetes/*`, `helm/*`, `docker-compose*` | `Dockerfile*`, `dockerignore` |
| **CI/CD** | `.github/workflows/*` | — |
| **Lockfiles** | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`, `go.sum`, `requirements.txt`, `pyproject.toml`, `Pipfile.lock`, `poetry.lock`, `pom.xml`, `build.gradle*`, `*.csproj`, `composer.lock`, `Gemfile.lock`, `mix.lock`, `rebar.lock` | — |
| **Config** | `*.proto` | `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `.env*`, `.gitignore`, `.editorconfig`, `Makefile*` |

**Add your own patterns** in `.agent-guard.json` — they merge with defaults.

---

## Security Considerations

### Threat Model

| Threat | Mitigation |
|--------|------------|
| **Command Injection** | Scripts use fixed `git` commands; user input only via `--target` (validated by Git) |
| **Path Traversal** | All paths resolved via `pathlib.Path`; logs written to `.agent-guard/logs/` only |
| **Config Tampering** | `.agent-guard.json` is local (gitignored); template is versioned |
| **Supply Chain** | Zero runtime dependencies — only Python stdlib |
| **Log Injection** | Logs are Markdown; user-controlled data escaped via f-strings |
| **Privilege Escalation** | Scripts run with user's permissions; no sudo, no network calls |

### Secure Usage Checklist

- [ ] Keep `.agent-guard.json` in `.gitignore` (prevents command injection via PR)
- [ ] Review `SKILL.md` before installing — it instructs your agent
- [ ] Verify install script (`install.sh`) before piping to bash
- [ ] Run verification commands locally before trusting auto-merge
- [ ] Audit `revert_cost_patterns` for your project's critical files

### What the Scripts CAN Do
- Run `git` read operations (`diff`, `log`, `merge-base`, `rev-parse`)
- Execute YOUR configured verification commands (lint, test, build)
- Write Markdown logs to `.agent-guard/logs/`

### What the Scripts CANNOT Do
- Push, commit, or modify Git history
- Access network (no HTTP, no Git remote writes)
- Read files outside the repository
- Execute arbitrary code beyond your configured commands

---

## Verified Agent Compatibility

| Agent | Install Method | Status |
|-------|---------------|--------|
| Cursor | `.cursorrules` append | ✅ Tested |
| Windsurf | `.windsurfrules` append | ✅ Tested |
| Claude Code | `.claude/skills/` | ✅ Tested |
| Aider | Prompt reference | ✅ Compatible |
| Generic CLI | Manual prompt | ✅ Compatible |

---

## Development (for THIS Repo Only)

> ⚠️ **This section is for contributors to git-flow-agent-guard itself.**  
> **Users of the skill do NOT need any of this.** Your project uses YOUR commands from `.agent-guard.json` — not ruff/mypy/pytest.

### Requirements
- Python 3.8+

### Running Verification Locally

```bash
# Install dev dependencies (for this repo only)
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

---

## Releasing

```bash
# Create release branch
git checkout -b release/v0.1.0

# Tag and push
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will build and create a GitHub Release automatically.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork and create a feature branch from `dev`
2. Make changes following the `SKILL.md` directives
3. Run `python scripts/evaluate-risk.py --target dev` — must pass
4. Open PR to `dev`

---

**Repository:** https://github.com/MessilineHani/git-flow-agent-guard