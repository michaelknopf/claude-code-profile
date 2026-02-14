---
description: Loop through an epic's tasks with Opus planning and Sonnet execution
argument-hint: <epic-id>
allowed-tools: Bash(bd:*), Bash(git:*), Task(*), Skill(*)
accepts-args: true
---

You are an orchestrator agent that processes all tasks in a beads epic sequentially using the **Opus→Sonnet pattern**: Opus plans each task, Sonnet executes it. Each sub-agent gets a clean context.

## Setup (Before Loop)

### Create Epic Branch
- Run: `git checkout -b epic/<epic-id>` (or similar branch name)
- If branch already exists, checkout existing branch
- Ensures all work is done on a dedicated branch, not main

## Loop Structure

Continue iterating until the epic is complete or all remaining tasks are blocked:

### A. Find Ready Work
- Run: `bd ready --parent <epic-id>`
- If no ready tasks exist:
  - Check if epic is complete (all child tasks closed)
  - If complete → report summary and exit with SUCCESS
  - If tasks exist but all blocked → report blockers and exit

### B. Select Task
- Choose the highest-priority ready task (P0 > P1 > P2 > P3 > P4)
- Announce which task you're working on

### C. Get Task Details
- Run: `bd show <task-id>`
- Parse the full task description and context

### D. Plan with Opus
- Spawn Task tool with:
  - subagent_type: "task-planner"
  - Prompt: Include the full task description

- The `task-planner` agent produces a structured plan with:
  - **Approach**: High-level strategy
  - **Files to Modify**: Specific file paths
  - **Implementation Steps**: Numbered, actionable steps
  - **Verification**: How to confirm success

### E. Output Plan Verbatim
**CRITICAL**: Display the complete Opus plan to the user before proceeding. The user must see the full plan for each task.

### F. Execute with Sonnet
- Spawn Task tool with:
  - model: "sonnet"
  - subagent_type: "general-purpose"
  - Prompt: Provide the full Opus plan and instruct: "Implement this plan exactly as specified."

### G. Close Task
- After successful implementation, run: `bd close <task-id> --reason "<brief summary>"`
- The summary should capture what was accomplished

### G2. Commit Changes
- Invoke: `/savi:commit` skill
- This creates an atomic commit for the completed sub-task

### H. Continue
- Return to step A for the next iteration
- Continue until the epic is complete or blocked

## Error Handling

- If a task fails during implementation, do NOT close it
- Report the failure to the user
- Ask whether to:
  - Skip to the next task
  - Retry with a different approach
  - Abort the epic loop

## Success Criteria

- All ready tasks in the epic are completed and closed
- The epic itself is complete (all child tasks resolved)
- Clear summary of work accomplished
