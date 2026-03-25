---
description: Pick a ready task and start working on it
allowed-tools: Read, Edit, Glob, Task(*)
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

Scan `docs/local/reports/` for any markdown report files that contain an unchecked item (`- [ ]`) in a `## Checklist` section.

If no unchecked items exist across all reports, report that there's nothing to pick up and suggest running an audit command to generate a new report.

## Phase 2: Select a Task

From all unchecked items across all reports, select the first one in the most recently modified report (reports are timestamped; newer = higher priority unless priority is embedded in the item). Apply judgment: skip items whose `**Dependencies:**` in the finding body lists items that are still unchecked.

## Phase 3: Get Task Details

Read the report file. Find the finding section that corresponds to the selected checklist item (match by number and title). Parse the full description, suggestion, and context.

## Phase 4: Execute

Treat the finding details as your prompt. Work on it exactly as you would any user request:
- Plan the work
- Read relevant files, understand context
- Implement the changes
- Run tests/checks as appropriate
- Follow all project conventions from CLAUDE.md

## Phase 5: Complete

When the task is done:
1. Edit the report file — change `- [ ] <number>. <title>` to `- [x] <number>. <title>  *(completed: <summary of what was done>)*`
2. Report what was accomplished

---

## Batch Mode (--loop flag)

Process up to 10 tasks per invocation:

1. **Find Ready Tasks**: Scan `docs/local/reports/` for unchecked items across all report files
2. **Check for Completion**: If no tasks are ready, report completion summary and exit
3. **Check Limit**: If 10 tasks have been completed this invocation, report summary and exit (more may remain)
4. **Select Task**: Choose the first unchecked item from the most recently modified report (skip items blocked by unchecked dependencies)
5. **Get Task Details**: Read the corresponding finding section from the report
6. **Spawn Sub-Agent**: Use the Task tool to spawn a sub-agent with:
   - The full finding details from the report
   - Instructions to implement the task and report what was done
   - Do NOT include `/next` in the prompt (avoid recursive skill loading)
7. **Mark Complete**: Edit the report file — change `- [ ]` to `- [x]` and append completion note
8. **Commit Changes**: Invoke `/savi:commit` skill to create an atomic commit for the completed task
9. **Repeat**: Go back to step 1 (completing tasks may unblock others)

### Completion Report

After the loop ends, report:
- Total number of tasks completed
- Brief summary of each task and what was accomplished
- Whether more ready tasks remain (if stopped due to limit)
