#!/usr/bin/env python3
"""
Render MCP template files by substituting environment variables.

Usage:
    python scripts/render_mcp_templates.py [--allow-missing] [--dry-run]

Environment Variables:
    CONTEXT7_API_KEY - API key for Context7 MCP server
    GITHUB_PAT       - GitHub Personal Access Token

The script will first load variables from .env file if it exists,
then fall back to shell environment variables.
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TemplateConfig:
    """Configuration for a template file and its output location."""

    template_path: Path
    output_path: Path


class TemplateRenderer:
    """
    Renders template files by substituting ${VAR} placeholders
    with environment variable values.
    """

    PLACEHOLDER_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")

    def __init__(self, allow_missing: bool = False):
        self.allow_missing = allow_missing
        self.missing_vars: set[str] = set()

    def render(self, template_content: str) -> str:
        """
        Substitute all ${VAR} placeholders with environment variable values.
        """

        def replace_var(match: re.Match[str]) -> str:
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                self.missing_vars.add(var_name)
                if self.allow_missing:
                    return match.group(0)
                return ""
            return value

        return self.PLACEHOLDER_PATTERN.sub(replace_var, template_content)

    def find_placeholders(self, template_content: str) -> set[str]:
        """Find all placeholder variable names in template content."""
        return set(self.PLACEHOLDER_PATTERN.findall(template_content))


def load_env_file(env_path: Path) -> None:
    """
    Load environment variables from .env file.
    Simple parser for KEY=VALUE format, ignoring comments and empty lines.
    """
    if not env_path.exists():
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value and value[0] in ('"', "'") and value[0] == value[-1]:
                value = value[1:-1]

            # Only set if not already in environment (shell env takes precedence)
            if key and key not in os.environ:
                os.environ[key] = value


def get_template_configs(project_root: Path) -> list[TemplateConfig]:
    """Return list of template configurations to process."""
    return [
        TemplateConfig(
            template_path=project_root / "plugins/savi/.mcp.template.json",
            output_path=project_root / "plugins/savi/.mcp.json",
        ),
        TemplateConfig(
            template_path=project_root / "plugins/savi/archive/.mcp.template.json",
            output_path=project_root / "plugins/savi/archive/.mcp.json",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render MCP template files with environment variable substitution."
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Allow missing environment variables (keep placeholders as-is)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print rendered content without writing files",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()

    # Load .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        load_env_file(env_file)
        print(f"Loaded environment from: {env_file}")

    configs = get_template_configs(project_root)
    renderer = TemplateRenderer(allow_missing=args.allow_missing)

    all_missing: set[str] = set()

    for config in configs:
        if not config.template_path.exists():
            print(f"Error: Template not found: {config.template_path}", file=sys.stderr)
            return 1

        template_content = config.template_path.read_text()
        rendered_content = renderer.render(template_content)
        all_missing.update(renderer.missing_vars)
        renderer.missing_vars.clear()

        if args.dry_run:
            print(f"=== {config.output_path} ===")
            print(rendered_content)
            print()
        else:
            config.output_path.parent.mkdir(parents=True, exist_ok=True)
            config.output_path.write_text(rendered_content)
            print(f"Rendered: {config.output_path}")

    if all_missing and not args.allow_missing:
        print(
            f"\nError: Missing environment variables: {', '.join(sorted(all_missing))}",
            file=sys.stderr,
        )
        return 1

    if all_missing and args.allow_missing:
        print(
            f"\nWarning: Some placeholders were not substituted: {', '.join(sorted(all_missing))}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
