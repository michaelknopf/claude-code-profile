---
description: Refactor code based on design principles, with codebase-wide discovery
argument-hint: <file>[:<lines>] [description]
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(python:*), Bash(mypy:*), Bash(ruff:*), Bash(pyright:*)
---

# /refactor — Principled Refactoring

**Target:** `$ARGUMENTS`

## Overview

This command helps you apply design principles (from `~/.claude/CLAUDE.md`) consistently across your codebase:
1. You point at code that smells or violates a principle
2. It finds similar violations elsewhere
3. Asks you to approve scope
4. Refactors all instances

## Phase 1: Understand the Issue

1. **Parse `$ARGUMENTS`** to extract:
   - Target file (required) - e.g., `src/api.py`
   - Line range (optional) - e.g., `src/api.py:42-50`
   - Description (optional) - e.g., `"these functions should be methods"`

2. **Read the target file/lines**

3. **Identify the issue**:
   - What design principle from `~/.claude/CLAUDE.md` is being violated?
   - Examples:
     - "Module-level functions with shared state → should be a class"
     - "Dict with fixed keys → should be a dataclass"
     - "Code in `__init__.py` → should move to a proper module"
     - "Re-exporting imports in `__init__.py` → imports should be direct"
   - What pattern should be searched for?

## Phase 2: Explore the Codebase

Spawn the `refactor-scout` agent with:
- The target file/lines
- The identified issue or pattern
- Instruction to search for similar violations across the codebase
- Reference to relevant principles from `~/.claude/CLAUDE.md`

The agent will return a concise inventory of all similar issues found.

## Phase 3: Decide Scope

Present the findings and ask the user via `AskUserQuestion`:

```
Found N similar issues:
1. src/foo.py:42-50 - module-level function with state (your target)
2. src/bar.py:15-30 - same pattern
3. src/utils.py:88-95 - similar, also uses global variable
4. src/helpers.py:12-40 - related function group

Options:
- Refactor all N instances
- Just the target file
- Let me pick specific files
```

**Important**: Always give the user control over scope.

## Phase 4: Execute Refactoring

For each file in the approved scope:

1. **Read the file** if not already read

2. **Apply the refactoring**:
   - Follow the relevant design principle
   - Make minimal changes (don't clean up unrelated code)
   - Preserve functionality
   - Update imports and references as needed

3. **Verify** (if tooling is available):
   - Run type checker: `mypy <file>` or `pyright <file>`
   - Run linter: `ruff check <file>`
   - Only proceed if checks pass

4. **Track the change** for the summary

## Phase 5: Summary

Report to the user:
- **Files modified**: List with line counts changed
- **Changes applied**: High-level description
- **Follow-ups**: Any manual steps needed (e.g., update tests, review logic)

## Guidelines

- **Respect principles**: Always reference and follow the design principles from `~/.claude/CLAUDE.md`
- **Minimal scope**: Don't refactor beyond what's needed to fix the identified issue
- **Ask for permission**: Large changes should be approved before execution
- **Verify**: Use linters/type checkers when available
- **Track changes**: Keep a running list of what was modified

## Examples

### Example 1: Module-level functions → Class
```
/refactor src/api/handlers.py:20-45 "these functions share state, should be a class"
```

### Example 2: Dict → Dataclass
```
/refactor src/models.py:12-20 "this dict has fixed keys, should be a dataclass"
```

### Example 3: Directory-wide search
```
/refactor src/utils/ "find all __init__.py files with code in them"
```

### Example 4: Implicit (let Claude figure it out)
```
/refactor src/legacy/processor.py "this file smells"
```
