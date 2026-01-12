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

## Included Commands

This plugin provides several powerful commands to enhance your Claude Code workflow.

### Command Categories

#### Analysis & Planning Commands (Read-Only)

These commands **do not make code changes**. They analyze your codebase and produce planning documents.

##### `/refactor-audit`
Scan codebase for design principle violations and generate prioritized refactoring backlog.
- **Output**: `docs/refactor-audit-YYYY-MM-DD.md` (+ conversation display)
- **Follow-up**: Use `/refactor` to apply recommended fixes
- **Example**: `/refactor-audit src/`

##### `/coverage-audit`
Analyze test coverage gaps and create prioritized test improvement plan.
- **Output**: `docs/coverage-audit-YYYY-MM-DD.md` (+ conversation display)
- **Follow-up**: Implement recommended test suites based on designs
- **Example**: `/coverage-audit coverage.json --top=5`

#### Implementation Commands

These commands **make code changes** or modify project state.

##### `/refactor`
Apply design principle-based refactoring to code (uses `/refactor-audit` findings).

##### `/commit`
Create contextual git commits. Automatically analyzes your changes and creates an appropriate commit message.

##### `/ci-debug`
Debug failing CI workflows and push fixes until they pass. Automatically follows workflow chains after fixes.

##### `/pr-reply`
Address, reply to, and resolve PR review comments with code changes. Streamlines the code review process.

##### `/debug`
Diagnose and fix command failures iteratively. Run a command and if it fails, diagnose the issue and make minimal changes until it succeeds (with bounded retries).

#### Documentation Commands

##### `/session-doc`
Generate a structured document summarizing the current session for future reference.

---

**Pro tip**: Run analysis commands (`/refactor-audit`, `/coverage-audit`) regularly to build improvement backlogs, then execute incrementally with implementation commands.

## Extending This Plugin

### Adding Custom Commands
Create `.md` files in the `plugins/savi/commands/` directory to add custom slash commands.

### Adding Agents
Create `.md` files in the `plugins/savi/agents/` directory to add specialized subagents.

### Adding Skills
Create skill directories with `SKILL.md` files in the `plugins/savi/skills/` directory.

### Adding Hooks
Add `hooks.json` configuration files in the `plugins/savi/hooks/` directory to respond to Claude Code events.
