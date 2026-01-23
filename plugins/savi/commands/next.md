---
description: Pick a ready task and start working on it
allowed-tools: Bash(bd:*)
---

# /next — Pick up the next ready task

## Phase 1: Find Ready Work

Run:
```bash
bd ready
```

If no tasks are ready, report that there's nothing to pick up and suggest checking `bd blocked` or creating a new issue.

## Phase 2: Select a Task

From the ready tasks, select the highest-priority one (P0 > P1 > P2 > P3 > P4). If multiple tasks share the same priority, use your judgment to pick the most impactful or logical next step (e.g., foundational work before dependent work, smaller unblocking tasks before larger ones).

## Phase 3: Claim the Task

1. Run `bd show <issue-id>` to get full task details (description, context, acceptance criteria)
2. Run `bd update <issue-id> --status in_progress` to claim it

## Phase 4: Execute

Treat the task description as your prompt. Work on it exactly as you would any user request:
- Plan the work using TodoWrite
- Read relevant files, understand context
- Implement the changes
- Run tests/checks as appropriate
- Follow all project conventions from CLAUDE.md

## Phase 5: Complete

When the task is done:
1. Run `bd close <issue-id> --reason "<summary of what was done>"`
2. Report what was accomplished
