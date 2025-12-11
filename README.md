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
HTTP-based MCP server providing advanced context management capabilities.
- **Type**: HTTP
- **URL**: https://mcp.context7.com/mcp

### Memory
Persistent memory and context management for Claude Code sessions. Store and recall information across conversations and projects.
- **Package**: `@modelcontextprotocol/server-memory`
- **Usage**: Automatically manages conversation context and memory

### Fetch
Web content fetching and data extraction capabilities. Access external APIs, scrape web content, and integrate external data sources.
- **Package**: `@modelcontextprotocol/server-fetch`
- **Usage**: Fetch web content and external data

### Terraform
Seamless integration with Terraform Registry APIs, enabling advanced automation and interaction capabilities for Infrastructure as Code (IaC) development.
- **Type**: Docker container
- **Image**: `hashicorp/terraform-mcp-server`
- **Usage**: Query Terraform modules, providers, and registry information

### Python SDK
Official Python SDK with FastMCP for rapid MCP development.
- **Module**: `python_sdk.server`
- **Usage**: Python-based MCP server development

## Directory Structure

```
.
├── .claude-plugin/
│   └── marketplace.json        # Plugin marketplace registration
├── .example.env                # Example environment variables (tracked)
├── .env                        # Your secrets (gitignored)
├── plugins/
│   └── main/
│       ├── .mcp.template.json  # MCP config template (tracked)
│       ├── .mcp.json           # Generated config (gitignored)
│       ├── archive/
│       │   ├── .mcp.template.json
│       │   └── .mcp.json
│       ├── commands/           # Custom slash commands
│       ├── agents/             # Custom agents (future)
│       ├── skills/             # Agent skills (future)
│       ├── hooks/              # Event hooks
│       └── plugin.json         # Plugin manifest
├── scripts/
│   └── render_mcp_templates.py # Template renderer
└── README.md                   # This file
```

## Extending This Plugin

### Adding Custom Commands
Create `.md` files in the `commands/` directory to add custom slash commands.

### Adding Agents
Create `.md` files in the `agents/` directory to add specialized subagents.

### Adding Skills
Create skill directories with `SKILL.md` files in the `skills/` directory.

### Adding Hooks
Add `hooks.json` configuration files in the `hooks/` directory to respond to Claude Code events.

## License

MIT
