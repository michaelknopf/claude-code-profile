---
description: Audit codebase for design principle violations and generate a report
argument-hint: [directory] [--output=<file>]
allowed-tools: Read, Glob, Grep
---

# /refactor-audit — Design Principle Compliance Audit

**Target:** `$ARGUMENTS`

## Overview

This command scans your codebase for design principle violations (from `~/.claude/CLAUDE.md`) and produces a prioritized report. The report is designed to be handed off to future Claude Code sessions for focused refactoring work.

Unlike `/refactor`, this command is **read-only** and makes no code changes. It produces a structured report identifying opportunities for improvement.

## Phase 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **Target directory** (optional) - e.g., `src/` or `plugins/savi/`
  - If not provided, audit entire codebase
- **Output file flag** (optional) - e.g., `--output=refactor-report.md`
  - If not provided, display report in conversation

## Phase 2: Load Design Principles

Read `~/.claude/CLAUDE.md` (and project-specific `CLAUDE.md` if exists) to understand:
- Design principles to check against
- Code patterns to look for
- Anti-patterns to identify

## Phase 3: Explore Codebase

Spawn the `refactor-scout` agent to scan the codebase for violations.

Pass to the agent:
- Target directory/scope
- Design principles to check
- Instruction to find ALL violations (not just similar to a target)
- Request categorization by principle/severity

The agent will return an inventory of all issues found.

## Phase 4: Present Findings

Show the user a summary of findings and ask them via `AskUserQuestion` what to include in the detailed report:

```
Found N refactoring opportunities across M files:

By principle:
- Module-level functions → OOP: 8 instances
- Dict with fixed keys → dataclass: 5 instances
- Code in __init__.py → proper modules: 3 instances
- Inheritance → composition: 2 instances

By priority (based on complexity, impact, coupling):
- High: 6 issues
- Medium: 9 issues
- Low: 3 issues

Options:
- Full report (all 18 issues)
- High priority only (6 issues) [Recommended]
- Medium and high priority (15 issues)
- Let me pick specific categories
```

**Important**: Give the user control over report scope to avoid overwhelming reports.

## Phase 5: Compile Report

Generate a structured markdown report with:

### Report Structure

```markdown
# Refactor Audit Report

Generated: YYYY-MM-DD
Scope: <directory or "entire codebase">
Principles: ~/.claude/CLAUDE.md

---

## Summary

Found N refactoring opportunities across M files.

| Priority | Category | Count |
|----------|----------|-------|
| High | Module-level functions → OOP | 4 |
| High | Code in __init__.py | 2 |
| Medium | Dict → dataclass | 5 |
| ... | ... | ... |

---

## High Priority

### 1. src/api/handlers.py:42-80 - Module-level functions with shared state

**Principle violated:** "Prefer object-oriented patterns over module-level functions and global variables"

**Description:**
The functions `process_request()`, `validate_input()`, `transform_data()`, and `send_response()` all share access to module-level variables `_cache` and `_config`. This creates implicit dependencies and makes testing difficult.

**Suggested approach:**
Extract into a `RequestHandler` class with `_cache` and `_config` as instance attributes. Make functions instance methods.

**Estimated effort:** Medium (4 functions, updates to call sites in 3 files)

**Handoff command:**
```
/refactor src/api/handlers.py:42-80 "convert to RequestHandler class"
```

---

### 2. src/__init__.py:1-45 - Business logic in package init

**Principle violated:** "Never put code in __init__.py files, unless there is a very specific reason"

**Description:**
The package `__init__.py` contains 45 lines of startup logic, configuration loading, and helper functions. This makes the package structure opaque and couples imports to side effects.

**Suggested approach:**
Move startup logic to `src/startup.py`, configuration to `src/config.py`, helpers to `src/utils.py`.

**Estimated effort:** Small (pure extraction, no logic changes needed)

**Handoff command:**
```
/refactor src/__init__.py "extract logic to proper modules"
```

---

[Continue for each issue in approved scope...]

---

## Next Steps

1. Copy any "Handoff command" above into a new Claude Code session
2. The `/refactor` command will find similar violations elsewhere
3. Approve scope and execute the refactoring
4. Run this audit again after changes to verify improvements
```

### Report Guidelines

- **One issue per heading** (numbered sequentially)
- **Include file:lines** in heading for easy navigation
- **Quote violated principles** from CLAUDE.md
- **Concrete descriptions** - what's wrong, why it matters
- **Actionable suggestions** - specific approach, not vague "improve this"
- **Effort estimates** - help user prioritize (Small/Medium/Large)
- **Handoff commands** - ready-to-run `/refactor` commands

## Phase 6: Output

If `--output` flag was provided:
- Write report to specified file
- Confirm: "Report written to `<file>`"

Otherwise:
- Display report in conversation

## Guidelines

- **Read-only**: Never make edits, only analyze and report
- **Reference principles**: Always quote specific principles from `~/.claude/CLAUDE.md`
- **Prioritize by value**: Consider complexity, impact, and coupling when ranking
- **Be concrete**: Avoid vague descriptions like "this could be better"
- **Handoff-ready**: Each issue should have a copy-paste-able `/refactor` command
- **Respect scope**: Only analyze what user approved
- **No false positives**: Better to miss issues than report non-issues

## Examples

### Example 1: Full codebase audit
```
/refactor-audit
```

### Example 2: Audit specific directory
```
/refactor-audit src/api/
```

### Example 3: Audit with output file
```
/refactor-audit --output=refactor-backlog.md
```

### Example 4: Audit multiple directories
```
/refactor-audit src/ tests/
```
