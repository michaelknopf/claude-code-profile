---
description: Pick a ready task and start working on it
allowed-tools: Bash(bd:*), Task(*)
accepts-args: true
---

# /next — Pick up the next ready task

## Mode Detection

Check if `--loop` flag is present in the args:
- If `--loop` is present: Use **Batch Mode** (process all ready tasks)
- Otherwise: Use **Single Task Mode** (process one task inline)

---

## Single Task Mode (Default)

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

---

## Batch Mode (--loop flag)

Process up to 10 tasks per invocation:

1. **Find Ready Tasks**: Run `bd ready` to get all ready tasks
2. **Check for Completion**: If no tasks are ready, report completion summary and exit
3. **Check Limit**: If 10 tasks have been completed this invocation, report summary and exit (more may remain)
4. **Select Task**: Choose the highest-priority task (P0 > P1 > P2 > P3 > P4)
5. **Get Task Details**: Run `bd show <issue-id>` to get full task details
6. **Spawn Sub-Agent**: Use the Task tool to spawn a sub-agent with:
   - The full task description from `bd show`
   - Instructions to implement the task and report what was done
   - Do NOT include `/next` in the prompt (avoid recursive skill loading)
7. **Close Task**: Run `bd close <issue-id> --reason "<summary from sub-agent>"`
8. **Repeat**: Go back to step 1 (completing tasks may unblock others)

### Completion Report

After the loop ends, report:
- Total number of tasks completed
- Brief summary of each task and what was accomplished
- Whether more ready tasks remain (if stopped due to limit)
