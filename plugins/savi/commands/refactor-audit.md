---
description: Audit codebase for design principle violations and generate a report
argument-hint: [directory] [--output=<file>] [--no-save]
allowed-tools: Read, Glob, Grep
---

# /refactor-audit — Design Principle Compliance Audit

**Target:** `$ARGUMENTS`

## ⚠️ What This Command Does

**This is a read-only analysis command.** It will:
- Scan your codebase for design principle violations (from `~/.claude/CLAUDE.md`)
- Generate a structured report with prioritized findings
- Provide actionable recommendations with handoff commands
- **NOT make any code changes**
- **NOT refactor or modify files**

**Related commands:**
- `/refactor-audit` - This command (analysis only)
- `/refactor` - Implements refactoring changes (use AFTER reviewing this audit)

## Output

**Default behavior**: Saves report to `docs/notes/reports/refactor-audit-YYYY-MM-DD-HH-MM.md` AND displays in conversation.

**Options**:
- `--output=<file>` - Save to custom location instead
- `--no-save` - Skip file creation, display in conversation only

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
- **Identify dependency relationships between findings**:
  - For each finding, note which other findings must complete first
  - Example: "Extract module X" must complete before "Update imports in Y"
  - Example: Converting a dict to a dataclass must happen before refactoring consumers of that dict
  - Consider file dependencies, import relationships, and shared state

The agent will return an inventory of all issues found with dependency information.

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

Generated: YYYY-MM-DD-HH-MM
Scope: <directory or "entire codebase">
Principles: ~/.claude/CLAUDE.md

---

## Checklist

- [ ] 1. src/api/handlers.py:42-80 - Convert to RequestHandler class
- [ ] 2. src/__init__.py:1-45 - Extract logic to proper modules

(One item per finding, in priority order. Completed items will be checked off during implementation.)

---

## Summary

Found N refactoring opportunities across M files.

| Priority | Category | Count |
|----------|----------|-------|
| High | Module-level functions → OOP | 4 |
| High | Code in __init__.py | 2 |
| Medium | Dict → dataclass | 5 |
| ... | ... | ... |

### Dependency Graph

Visual representation of task dependencies (arrows show blocking relationships):

```
#1 → #3 → #5
#2 (independent)
#4 → #6, #7
```

**Legend:**
- `#1 → #3` means "#1 must complete before #3 can start"
- `(independent)` means the task has no dependencies

---

## High Priority

### 1. src/api/handlers.py:42-80 - Module-level functions with shared state

**Principle violated:** "Prefer object-oriented patterns over module-level functions and global variables"

**Description:**
The functions `process_request()`, `validate_input()`, `transform_data()`, and `send_response()` all share access to module-level variables `_cache` and `_config`. This creates implicit dependencies and makes testing difficult.

**Suggested approach:**
Extract into a `RequestHandler` class with `_cache` and `_config` as instance attributes. Make functions instance methods.

<!-- plan:skip is NOT appropriate here — restructuring to a class requires planning -->

**Estimated effort:** Medium (4 functions, updates to call sites in 3 files)

**Dependencies:**
- Blocks: #3 (consumers must be updated after this refactoring)
- Independent of other refactorings

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

<!-- plan:skip -->

**Estimated effort:** Small (pure extraction, no logic changes needed)

**Dependencies:**
- Independent of other refactorings

**Handoff command:**
```
/refactor src/__init__.py "extract logic to proper modules"
```

---

[Continue for each issue in approved scope...]

---

## Next Steps

**📋 This report is complete. No code changes have been made.**

To implement these recommendations, run:

```bash
/savi:epic-loop <path-to-this-report>
```

This will work through the checklist above sequentially, planning and executing each item.

**Manual option:** Copy any "Handoff command" above into the chat to implement individually.
```

### Report Guidelines

- **One issue per heading** (numbered sequentially)
- **Include file:lines** in heading for easy navigation
- **Quote violated principles** from CLAUDE.md
- **Concrete descriptions** - what's wrong, why it matters
- **Actionable suggestions** - specific approach, not vague "improve this"
- **Effort estimates** - help user prioritize (Small/Medium/Large)
- **Handoff commands** - ready-to-run `/refactor` commands
- **plan:skip marker** - Add `<!-- plan:skip -->` inside a finding's detail section when **all** of these are true:
  - The fix is mechanical — no design decisions or trade-offs to evaluate
  - The description already specifies exactly what to change (file, location, concrete transformation)
  - The change affects 1-2 files at most
  - Examples: extract code from `__init__.py` to a named module, rename a variable, delete an unused import

  Do **not** add `plan:skip` when:
  - The fix requires creating new abstractions (classes, modules) that consumers then need to adopt
  - Multiple valid approaches exist (e.g., composition vs delegation vs strategy pattern)
  - The description says "consider" or "evaluate" rather than prescribing a specific change

  When in doubt, omit the marker. An unnecessary planning phase wastes less than a failed unplanned execution.

## Phase 6: Output

**Default**: Save report to `docs/notes/reports/refactor-audit-{YYYY-MM-DD-HH-MM}.md` AND display in conversation

**Steps**:
1. Ensure `docs/notes/reports/` directory exists (create if needed)
2. Generate timestamped filename: `refactor-audit-{YYYY-MM-DD-HH-MM}.md`
3. Write report to file
4. Display report in conversation
5. Show confirmation: "Report saved to `docs/notes/reports/refactor-audit-2026-01-11-14-30.md`. To implement, run: `/savi:epic-loop docs/notes/reports/refactor-audit-2026-01-11-14-30.md`"

**If `--output=<file>` specified**:
- Use custom path instead of default
- Create parent directories if needed

**If `--no-save` specified**:
- Skip file writing
- Display report in conversation only

## Guidelines

- **Read-only**: Never make edits, only analyze and report
- **Reference principles**: Always quote specific principles from `~/.claude/CLAUDE.md`
- **Prioritize by value**: Consider complexity, impact, and coupling when ranking
- **Be concrete**: Avoid vague descriptions like "this could be better"
- **Handoff-ready**: Each issue should have a copy-paste-able `/refactor` command
- **Respect scope**: Only analyze what user approved
- **No false positives**: Better to miss issues than report non-issues

## Examples

### Example 1: Full codebase audit (saves to docs/notes/reports/refactor-audit-YYYY-MM-DD-HH-MM.md)
```
/refactor-audit
```

### Example 2: Audit specific directory
```
/refactor-audit src/api/
```

### Example 3: Custom output location
```
/refactor-audit --output=backlog/refactor-tasks.md
```

### Example 4: Display only (no file)
```
/refactor-audit --no-save
```

### Example 5: Audit multiple directories
```
/refactor-audit src/ tests/
```
