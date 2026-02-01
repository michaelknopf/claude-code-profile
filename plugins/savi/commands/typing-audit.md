---
description: Audit Python codebase for type safety opportunities (dicts vs typed structures, Any types)
argument-hint: [directory] [--output=<file>] [--no-save]
allowed-tools: Read, Glob, Grep, Bash(bd:*)
---

# /typing-audit — Python Type Safety Audit

**Target:** `$ARGUMENTS`

## ⚠️ What This Command Does

**This is a read-only analysis command.** It will:
- Scan Python code for type safety opportunities
- Find dicts with string keys that should be pydantic models, dataclasses, or TypedDicts
- Identify uses of `Any` that could be narrowed to specific types
- Generate a structured report with prioritized findings
- **NOT make any code changes**
- **NOT refactor or modify files**

**Related commands:**
- `/typing-audit` - This command (analysis only)
- `/refactor` - Implements refactoring changes (use AFTER reviewing this audit)

## Output

**Default behavior**: Saves report to `docs/notes/typing-audit-YYYY-MM-DD.md` AND displays in conversation.

**Options**:
- `--output=<file>` - Save to custom location instead
- `--no-save` - Skip file creation, display in conversation only

## Overview

This command scans your Python codebase for opportunities to improve type safety. It identifies:
1. Dicts with string keys that should be typed structures
2. Overuse of `Any` type hints that could be more specific

The report is designed to be handed off to future Claude Code sessions for focused refactoring work.

Unlike `/refactor`, this command is **read-only** and makes no code changes. It produces a structured report identifying opportunities for improvement.

## Phase 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **Target directory** (optional) - e.g., `src/` or `lib/`
  - If not provided, audit entire codebase
- **Output file flag** (optional) - e.g., `--output=type-report.md`
  - If not provided, use default location
- **No-save flag** (optional) - e.g., `--no-save`
  - If provided, display report in conversation only

## Phase 2: Load Type Principles

Read the type safety principles document to understand patterns to detect:

**Primary source:** `plugins/savi/docs/type-safety-principles.md`

Use Oracle MCP or direct Read to load the document. Extract key principles:
- Fixed-key data belongs in structured types (not dicts)
- Stub files are all-or-nothing (prefer wrappers)
- Isolate type workarounds (DRY for casts/ignores)
- Use generic types with inline `[T]` syntax (Python 3.12+)
- Use modern `type` keyword for aliases
- Minimize and specify type ignores

Also reference `~/.claude/CLAUDE.md` for any project-specific type conventions.

## Phase 3: Explore Codebase

Spawn the `typing-scout` agent to scan the codebase for type safety issues.

Pass to the agent:
- Target directory/scope
- Type principles to check
- Instruction to find ALL type safety issues (both dict patterns and Any types)
- Request categorization by type and severity
- **Identify dependency relationships between findings**:
  - For each finding, note which other findings must complete first
  - Example: Converting a dict to a dataclass must happen before refactoring consumers of that dict
  - Example: "Update type hint in module X" must complete before "Update callers in module Y"
  - Consider file dependencies, import relationships, and shared state

The agent will return an inventory of all issues found with dependency information.

## Phase 4: Present Findings

Show the user a summary of findings and ask them via `AskUserQuestion` what to include in the detailed report:

```
Found N type safety issues across M files:

By category:
- Dict → typed structure: 12 instances
- Any → specific type: 8 instances

By priority (based on usage frequency, API surface, impact):
- High: 7 issues
- Medium: 10 issues
- Low: 3 issues

Options:
- Full report (all 20 issues)
- High priority only (7 issues) [Recommended]
- Medium and high priority (17 issues)
- Let me pick specific categories
```

**Important**: Give the user control over report scope to avoid overwhelming reports.

## Phase 5: Compile Report

Generate a structured markdown report with:

### Report Structure

```markdown
# Typing Audit Report

Generated: YYYY-MM-DD
Scope: <directory or "entire codebase">
Principles: ~/.claude/CLAUDE.md

---

## Summary

Found N type safety issues across M files.

| Priority | Category | Count |
|----------|----------|-------|
| High | Dict → typed structure | 5 |
| High | Any → specific type | 2 |
| Medium | Dict → TypedDict | 7 |
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

### 1. src/api/handlers.py:42 - Dict[str, Any] return type

**Principle violated:** "Prefer pydantic models or dataclasses over dictionaries to represent static types"

**Description:**
The `get_user_data()` function returns `Dict[str, Any]`, but the dictionary has a fixed structure with keys: "id", "name", "email", "role". This return type loses type safety - callers can't benefit from type checking and autocomplete.

**Current code:**
```python
def get_user_data(user_id: int) -> Dict[str, Any]:
    return {
        "id": user_id,
        "name": db.get_name(user_id),
        "email": db.get_email(user_id),
        "role": db.get_role(user_id)
    }
```

**Suggested approach:**
Create a `UserData` pydantic model or dataclass with typed fields. This provides:
- Type safety for consumers
- IDE autocomplete
- Runtime validation (if using pydantic)
- Clear API contract

**Estimated effort:** Small (single function, straightforward conversion)

**Dependencies:**
- Blocks: #3 (consumers must be updated after this refactoring)
- Independent of other refactorings

**Handoff command:**
```
/refactor src/api/handlers.py:42 "convert Dict[str, Any] return to UserData model"
```

---

### 2. src/config.py:15-20 - dict literal with fixed keys

**Principle violated:** "Prefer pydantic models or dataclasses over dictionaries to represent static types"

**Description:**
The `DEFAULT_CONFIG` dictionary has fixed keys and known value types, but is typed as `dict`. This pattern appears throughout the file with 3 similar config dicts.

**Current code:**
```python
DEFAULT_CONFIG = {
    "timeout": 30,
    "retries": 3,
    "base_url": "https://api.example.com",
    "verify_ssl": True
}
```

**Suggested approach:**
Convert to a `Config` dataclass or pydantic model. Consider making it frozen/immutable.

**Estimated effort:** Medium (3 similar dicts to convert, need to update all usage sites)

**Dependencies:**
- Independent of other refactorings

**Handoff command:**
```
/refactor src/config.py:15-20 "convert config dicts to Config dataclass"
```

---

[Continue for each issue in approved scope...]

---

## Next Steps

**📋 This report is complete. No code changes have been made.**

To implement these recommendations:

1. **Review priorities** - Focus on High priority issues first
2. **Copy handoff commands** - Each issue includes a ready-to-run `/refactor` command
3. **Execute incrementally** - Don't try to fix everything at once
   ```bash
   # Example: Implement the first refactoring
   /refactor src/api/handlers.py:42 "convert Dict[str, Any] return to UserData model"
   ```
4. **Verify improvements** - Re-run audit after changes:
   ```bash
   /typing-audit src/
   ```
5. **Track progress** - Compare new report with this one to measure improvements

**Need help implementing?** Copy any "Handoff command" above into the chat.
```

### Report Guidelines

- **One issue per heading** (numbered sequentially)
- **Include file:lines** in heading for easy navigation
- **Quote violated principles** from CLAUDE.md
- **Concrete descriptions** - what's wrong, why it matters
- **Show current code** - snippet of the problematic pattern
- **Actionable suggestions** - specific approach, not vague "improve this"
- **Explain benefits** - why the typed version is better
- **Effort estimates** - help user prioritize (Small/Medium/Large)
- **Dependencies** - list tasks this blocks or is blocked by
- **Handoff commands** - ready-to-run `/refactor` commands

## Phase 6: Beads Integration (if available)

Check if beads is initialized in the current repository:

```bash
bd info --json 2>/dev/null
```

If beads is available (command succeeds), integrate findings with beads issue tracker:

### 6.1: Create Epic

Create an epic to track the audit:

```bash
bd create "Typing Audit: <scope> (<YYYY-MM-DD>)" -t epic -p 2 --json
```

Extract the epic ID from the JSON response for use in subsequent steps.

### 6.2: Create Subtasks

For each finding in the report, create a subtask:

```bash
bd create "<short-title>" -t task -p <priority> --parent <epic-id> \
  -d "**Principle:** <violated principle>

**Location:** <file:lines>

**Description:** <description>

**Command:** /savi:refactor <file:lines> \"<description>\"" --json
```

**Priority mapping:**
- High priority findings → `1`
- Medium priority findings → `2`
- Low priority findings → `3`

**Short title format:** `<file> - <brief-description>`
- Example: `handlers.py - Convert Dict to UserData model`
- Keep titles under 60 characters

Extract task IDs from JSON responses and map them to report issue numbers (e.g., issue #1 → task_id_1).

### 6.3: Set Dependencies

For each finding that has dependencies (from the Dependencies section in the report):

```bash
bd dep add <prerequisite-task-id> <dependent-task-id> --type blocks
```

**Important:** Only create blocking dependencies. Related tasks that don't block each other should remain independent.

### 6.4: Sync to Remote

Synchronize the issues to the remote repository:

```bash
bd sync
```

### 6.5: Report to User

Display a summary of the beads integration:

```
✅ Created epic <epic-id> with N subtasks in beads.

To execute these refactorings:
1. Run `bd ready` to see unblocked tasks
2. Run `/savi:next --loop` in a new session to process all ready tasks automatically
3. Or pick individual tasks with `/savi:next` (processes one at a time)

Track progress:
- `bd stats` - View completion statistics
- `bd blocked` - See tasks waiting on dependencies
- `bd show <epic-id>` - View full epic details
```

### 6.6: Skip if Beads Not Available

If `bd info` fails (beads not initialized), skip this phase silently and proceed to Phase 7. Do not display any error or warning about beads.

## Phase 7: Output

**Default**: Save report to `docs/notes/typing-audit-{YYYY-MM-DD}.md` AND display in conversation

**Steps**:
1. Ensure `docs/notes/` directory exists (create if needed)
2. Generate timestamped filename: `typing-audit-{YYYY-MM-DD}.md`
3. Write report to file
4. Display report in conversation
5. Show confirmation: "📄 Report saved to `docs/notes/typing-audit-2026-01-11.md`"

**If `--output=<file>` specified**:
- Use custom path instead of default
- Create parent directories if needed

**If `--no-save` specified**:
- Skip file writing
- Display report in conversation only

## Guidelines

- **Read-only**: Never make edits, only analyze and report
- **Reference principles**: Always quote specific principles from `~/.claude/CLAUDE.md`
- **Prioritize by value**: Consider usage frequency, API surface, and maintainability impact
- **Be concrete**: Avoid vague descriptions like "this could be better"
- **Show code**: Include snippets of current code and suggested typed version
- **Handoff-ready**: Each issue should have a copy-paste-able `/refactor` command
- **Respect scope**: Only analyze what user approved
- **No false positives**: Better to miss issues than report non-issues (e.g., dict[str, Any] is valid for truly dynamic data)

## Examples

### Example 1: Full codebase audit (saves to docs/notes/typing-audit-YYYY-MM-DD.md)
```
/typing-audit
```

### Example 2: Audit specific directory
```
/typing-audit src/api/
```

### Example 3: Custom output location
```
/typing-audit --output=backlog/type-improvements.md
```

### Example 4: Display only (no file)
```
/typing-audit --no-save
```

### Example 5: Audit multiple directories
```
/typing-audit src/ lib/
```

## Common Patterns to Detect

### Dict → Typed Structure

**Pattern 1: Dict[str, Any] return types**
```python
def get_user() -> Dict[str, Any]:  # ❌
    return {"id": 1, "name": "Alice"}

# Should be:
@dataclass
class User:
    id: int
    name: str

def get_user() -> User:  # ✅
    return User(id=1, name="Alice")
```

**Pattern 2: Dict literals with fixed keys**
```python
config = {  # ❌
    "timeout": 30,
    "retry": 3
}

# Should be:
@dataclass
class Config:
    timeout: int
    retry: int

config = Config(timeout=30, retry=3)  # ✅
```

**Pattern 3: JSON parsing without models**
```python
data = json.loads(response.text)  # ❌ returns dict
process(data["user"]["name"])

# Should be:
class UserResponse(BaseModel):
    user: User

data = UserResponse.model_validate_json(response.text)  # ✅
process(data.user.name)
```

### Any → Specific Type

**Pattern 1: Any in type hints**
```python
def process(data: Any) -> Any:  # ❌
    return data.upper()

# Should be:
def process(data: str) -> str:  # ✅
    return data.upper()
```

**Pattern 2: Generic containers with Any**
```python
records: List[Any] = fetch_records()  # ❌

# Should be:
records: List[Record] = fetch_records()  # ✅
```
