---
description: Break down an arbitrary task into a checklist report for epic-loop
argument-hint: <task description> [--output=<file>] [--no-save]
allowed-tools: Read, Glob, Grep, AskUserQuestion
accepts-args: true
---

# /savi:breakdown — Task Breakdown

**Task:** `$ARGUMENTS`

## What This Command Does

Takes a free-form task description, explores the codebase, and produces a structured report with a `## Checklist` of discrete subtasks. The report is in the same format as `/refactor-audit` and `/typing-audit` outputs, so `/savi:epic-loop` can consume it directly.

**This command does NOT make any code changes.**

## Phase 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **Task description** — everything before any `--` flags (required)
- `--output=<file>` — save to custom path instead of default
- `--no-save` — display in conversation only, skip file creation

## Phase 2: Explore the Codebase

Use Glob, Grep, and Read to understand what's relevant to the task. The goal is to find:
- Files and directories most likely affected by the task
- Existing patterns and abstractions to follow (or extend)
- Anything already implemented that relates to the task
- Entry points, interfaces, and integration boundaries

Focus your exploration. You don't need to read everything — read what's relevant to decomposing the work.

## Phase 3: Decompose into Subtasks

Break the task into discrete, ordered subtasks. Each subtask must:
- Be independently implementable and committable (atomic unit of work)
- Have a specific file (or files) and a brief title
- Be concrete enough that another agent can execute it without making major decisions

**Decomposition guidelines:**
- Order subtasks by their dependency chain — foundational changes first, consumers after
- Each subtask should affect a small number of files (ideally 1-3)
- Separate concerns: don't bundle unrelated changes into one subtask
- If a subtask is purely mechanical (no design decisions), note it — it will get `<!-- plan:skip -->` in the report
- Identify which subtasks block others and document that explicitly

**Effort sizing:**
- **Small** — straightforward change, 1-2 files, no design decisions (<30 min)
- **Medium** — some complexity, a few files, minor design choices (30-90 min)
- **Large** — complex change, many files, significant design decisions (>90 min)

## Phase 4: Present Summary

Show the user a summary and ask for approval:

```
Task: <task description>

Proposed subtasks (N total):

1. path/to/file.py - Brief title [Small]
2. path/to/other.py - Brief title [Medium]
   ↳ depends on #1
3. path/to/another.py - Brief title [Small] (mechanical)
...

Options:
- Proceed with all N subtasks
- Remove some subtasks
- Add or modify subtasks
```

Use `AskUserQuestion` to get approval or adjustments. If the user wants changes, apply them before generating the report.

## Phase 5: Compile Report

Generate the report in this exact format:

```markdown
# Task Plan Report

Task: <task description>
Generated: YYYY-MM-DD-HH-MM

---

## Checklist

- [ ] 1. path/to/file.py - Brief title
- [ ] 2. path/to/other.py - Brief title
- [ ] 3. path/to/another.py - Brief title

---

## Summary

<1-2 sentence description of the overall approach and what will change>

### Dependency Graph

```
#1 → #2
#3 (independent)
```

**Legend:** `#1 → #2` means "#1 must complete before #2 can start"

---

## Tasks

### 1. path/to/file.py - Brief title

**Description:**
What needs to be done and why.

**Suggested approach:**
Specific, concrete instructions for how to implement it. Reference existing patterns or functions by name.

<!-- plan:skip -->   (include ONLY for mechanical tasks — see criteria below)

**Estimated effort:** Small

**Dependencies:**
- Blocks: #2
- Independent of other tasks

---

### 2. path/to/other.py - Brief title

...

---

## Next Steps

**No code changes have been made.**

To implement these tasks, run:

```bash
/savi:epic-loop <path-to-this-report>
```

This will work through the checklist sequentially, planning and executing each task.
```

### When to add `<!-- plan:skip -->`

Add it when **all** of the following are true:
- The fix is mechanical — no design decisions or trade-offs
- The suggested approach specifies exactly what to change (file, location, transformation)
- The change affects 1-2 files at most
- Examples: rename a variable, delete unused code, move a function, update a config value

Do **not** add it when:
- The task requires creating new abstractions (classes, modules, interfaces)
- Multiple valid approaches exist
- The description says "consider" or "evaluate" rather than prescribing a specific change

When in doubt, omit the marker.

## Phase 6: Save Report

**Default**: Save to `docs/notes/reports/breakdown-{YYYY-MM-DD-HH-MM}.md` AND display in conversation.

Steps:
1. Ensure `docs/notes/reports/` directory exists (create if needed)
2. Generate timestamped filename: `breakdown-{YYYY-MM-DD-HH-MM}.md`
3. Write report to file
4. Display in conversation
5. Show: "Report saved to `docs/notes/reports/breakdown-2026-01-11-14-30.md`. To implement, run: `/savi:epic-loop docs/notes/reports/breakdown-2026-01-11-14-30.md`"

**If `--output=<file>`**: Use custom path instead.

**If `--no-save`**: Skip file writing, display only.

## Examples

```
/savi:breakdown "add a health check endpoint"
/savi:breakdown "migrate authentication from sessions to JWTs"
/savi:breakdown "add pagination to the user listing API" --output=docs/notes/reports/pagination.md
/savi:breakdown "extract the email sending logic into a standalone service" --no-save
```
