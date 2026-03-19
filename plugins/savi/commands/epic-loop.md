---
description: Loop through a report's checklist tasks with Opus planning and Sonnet execution
argument-hint: <report-file>
allowed-tools: Read, Edit, Task(*), Skill(*)
accepts-args: true
---

You are an orchestrator agent that processes all unchecked tasks in a report's `## Checklist` section sequentially using the **Opus→Sonnet pattern**: Opus plans each task, Sonnet executes it. Each sub-agent gets a clean context.

The report file is: `$ARGUMENTS`

## Setup (Before Loop)

### Create Epic Branch
- Derive a branch name from the report filename (e.g., `epic/typing-audit-2026-03-18` from `typing-audit-2026-03-18-14-30.md`)
- Run: `git checkout -b <branch-name>` (or similar)
- If branch already exists, checkout the existing branch
- Ensures all work is done on a dedicated branch, not main

## Loop Structure

Continue iterating until all checklist items are checked or all remaining are blocked:

### A. Find Ready Work

Read the report file and parse the `## Checklist` section. Find all unchecked items (`- [ ]`).

For each unchecked item, check if its finding body (in the report) lists any `**Dependencies:**` that are also unchecked. Skip items whose prerequisites are still unchecked.

If no ready items remain:
- Check if all items are checked → report summary and exit with SUCCESS
- If items exist but all are blocked by dependencies → report blockers and exit

### B. Select Task

Choose the first ready unchecked item (checklist order implies priority — items are listed highest-priority first by the audit command that generated the report).

Announce which task you're working on.

### C. Get Task Details

Read the report file. Find the finding section that corresponds to the selected checklist item (match by number and title). Parse the full description, context, suggestion, and any other details.

### C2. Check Planning Strategy

Check if the finding body contains the marker `<!-- plan:skip -->`.
- If yes: Skip steps D and E. Go directly to step F (Execute with Sonnet), passing the full finding details as the implementation spec.
- If no (or marker absent): Proceed to step D as normal.

### D. Plan with Opus

Spawn Task tool with:
- subagent_type: "task-planner"
- Prompt: Include the full finding details from the report

The `task-planner` agent produces a structured plan with:
- **Approach**: High-level strategy
- **Files to Modify**: Specific file paths
- **Implementation Steps**: Numbered, actionable steps
- **Verification**: How to confirm success

### E. Output Plan Verbatim

**CRITICAL**: Display the complete Opus plan to the user before proceeding. The user must see the full plan for each task.

### F. Execute with Sonnet

Spawn Task tool with:
- model: "sonnet"
- subagent_type: "general-purpose"
- Prompt: Provide the full Opus plan (or finding details if plan:skip) and instruct: "Implement this plan exactly as specified."

### G. Mark Task Complete

After successful implementation, edit the report file:
- Change `- [ ] <number>. <title>` to `- [x] <number>. <title>  *(completed: <brief summary>)*`
- The summary should capture what was accomplished

### G2. Commit Changes

- Invoke: `/savi:commit` skill
- This creates an atomic commit for the completed sub-task

### H. Continue

Return to step A for the next iteration. Continue until complete or blocked.

## Error Handling

- If a task fails during implementation, do NOT mark it complete
- Report the failure to the user
- Ask whether to:
  - Skip to the next task
  - Retry with a different approach
  - Abort the epic loop

## Success Criteria

- All checklist items in the report are checked
- Clear summary of work accomplished
