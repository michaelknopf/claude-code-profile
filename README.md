# Michael Knopf's Claude Code Profile

Personal Claude Code plugin with integrated MCP servers, presets, and team-shareable configurations.

## Overview

This plugin provides a centralized configuration for Claude Code that can be version-controlled and shared with team members. It includes several powerful MCP servers that extend Claude's capabilities.

## Installation

To install this plugin:

```bash
# Clone the repository
git clone https://github.com/michaelknopf/claude-code-profile.git

# Link the plugin to Claude Code
# (Follow Claude Code plugin installation instructions)
```

## MCP Configuration Setup

This plugin uses a templating system to keep secrets out of version control. MCP configuration files (`.mcp.json`) are generated from template files.

### Initial Setup

1. **Copy the example environment file:**
   ```bash
   cp .example.env .env
   ```

2. **Edit `.env` with your API keys**

3. **Generate the MCP configuration files:**
   ```bash
   python scripts/render_mcp_templates.py
   ```

### Updating Configuration

After modifying template files (`.mcp.template.json`), regenerate the config files:

```bash
python scripts/render_mcp_templates.py
```

### Script Options

- `--dry-run` - Preview output without writing files
- `--allow-missing` - Allow missing environment variables (keeps placeholders)

Example:
```bash
# Preview what will be generated
python scripts/render_mcp_templates.py --dry-run

# Generate with some missing variables
python scripts/render_mcp_templates.py --allow-missing
```

## Included MCP Servers

### Context7
HTTP-based MCP server providing up-to-date documentation and code examples for programming libraries and frameworks.
- **Type**: HTTP
- **URL**: https://mcp.context7.com/mcp

## Commands

### Analysis & Auditing (Read-Only)

These commands analyze your codebase and produce planning documents without making code changes.

##### `/refactor-audit`
Scan codebase for design principle violations and generate a prioritized refactoring backlog.
- **Output**: `docs/notes/refactor-audit-YYYY-MM-DD.md`
- **Follow-up**: Use `/refactor` to apply recommended fixes
- **Example**: `/refactor-audit src/`

##### `/coverage-audit`
Analyze test coverage gaps and create a prioritized test improvement plan.
- **Output**: `docs/notes/coverage-audit-YYYY-MM-DD.md`
- **Example**: `/coverage-audit coverage.json --top=5`

##### `/typing-audit`
Audit Python codebase for type safety issues — dicts that should be typed structures, overuse of `Any`, and other patterns.
- **Output**: `docs/notes/typing-audit-YYYY-MM-DD.md`
- **Example**: `/typing-audit src/`

##### `/review-pr`
Review the current branch's PR diff and produce a prioritized audit report of bugs, security issues, design problems, and more.
- **Output**: `docs/notes/review-pr-{BRANCH}-YYYY-MM-DD.md`
- **Example**: `/review-pr`

##### `/smoke`
Design or audit smoke tests using established principles. Two modes: `design` (create new tests) and `audit` (review existing tests).
- **Example**: `/smoke design src/api/`

### Fixing & Implementation

These commands make code changes or modify project state.

##### `/fix`
Run a command; if it fails, diagnose and make minimal changes until it succeeds (bounded retries). Intelligently routes type errors to the `type-fix-planner` agent and other errors to the `fix-diagnostician` agent.
- **Example**: `/fix just test`

##### `/ci-fix`
Debug failing CI workflows and push fixes until they pass. Automatically follows workflow chains and routes to specialized agents based on error type.
- **Example**: `/ci-fix 123`

##### `/refactor`
Apply design principle-based refactoring with codebase-wide discovery of similar violations.
- **Example**: `/refactor src/api/handlers.py:42-80 "convert to RequestHandler class"`

##### `/py-dep-upgrade`
Remove upper bounds from Python dependencies and upgrade to latest versions, fixing any resulting issues.
- **Example**: `/py-dep-upgrade`

##### `/pr-reply`
Address, reply to, and resolve PR review comments with code changes.
- **Example**: `/pr-reply all`

### Task Orchestration

Commands for working through structured task backlogs (integrates with beads issue tracker).

##### `/next`
Pick up the next ready task and work on it. Use `--loop` to process up to 10 tasks in batch mode.
- **Example**: `/next` or `/next --loop`

##### `/epic-loop`
Loop through all tasks in a beads epic using the Opus→Sonnet pattern: the `task-planner` agent plans each task, then a Sonnet agent executes it.
- **Example**: `/epic-loop EPIC-1`

### Documentation

##### `/doc`
Generate high-level conceptual documentation for a file or folder, focusing on the "why" rather than the "what."
- **Example**: `/doc src/api/ --output=docs/api-architecture.md`

##### `/doc-refresh`
Update existing conceptual documentation to reflect the current state of the code it describes.
- **Example**: `/doc-refresh docs/api-architecture.md`

##### `/session-doc`
Generate a structured document summarizing the current session for future reference.
- **Example**: `/session-doc ~/Documents/sessions`

### Workflow

##### `/commit`
Create contextual git commits. Analyzes your changes and generates an appropriate commit message.

---

**Pro tip**: Run analysis commands (`/refactor-audit`, `/coverage-audit`, `/typing-audit`) regularly to build improvement backlogs, then execute incrementally with `/refactor`, `/fix`, or `/next --loop`.

## Agents

Commands spawn specialized agents via the Task tool for domain-specific diagnosis and planning. Key agents:

| Agent | Model | Used By | Purpose |
|-------|-------|---------|---------|
| `fix-diagnostician` | Opus | `/fix`, `/ci-fix` | General build/test failure diagnosis |
| `type-fix-planner` | Opus | `/fix`, `/ci-fix`, `/py-dep-upgrade` | Type error diagnosis using type safety principles |
| `task-planner` | Opus | `/epic-loop` | Structured implementation planning |
| `test-suite-planner` | Opus | `/coverage-audit` | Test suite design for coverage gaps |
| `refactor-scout` | Sonnet | `/refactor-audit`, `/refactor` | Codebase-wide pattern/violation search |
| `typing-scout` | Sonnet | `/typing-audit` | Type safety issue discovery |

## Extending This Plugin

### Adding Custom Commands
Create `.md` files in the `plugins/savi/commands/` directory to add custom slash commands.

### Adding Agents
Create `.md` files in the `plugins/savi/agents/` directory to add specialized subagents that commands can spawn via the Task tool.

### Adding Skills
Create skill directories with `SKILL.md` files in the `plugins/savi/skills/` directory for reusable task implementations.

### Adding Hooks
Add `hooks.json` configuration files in the `plugins/savi/hooks/` directory to respond to Claude Code events.

### Principle Documents
Add `.md` files to `plugins/savi/docs/` to define principles that agents reference during analysis. Current documents:
- `type-safety-principles.md` — Used by `type-fix-planner` and `typing-scout`
- `smoke-test-principles.md` — Used by `/smoke`
