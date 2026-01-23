---
description: Debug failing CI workflows and push fixes until they pass
argument-hint: "[PR# | branch | run-id]"
allowed-tools: Bash(gh:*), Bash(just:*), Bash(git:*), Read, Edit, Write, Glob, Grep
---

# /ci-debug — Debug and fix CI failures

**Target:** $ARGUMENTS (defaults to current branch's PR if empty)

## Phase 1: Identify the Failing Workflow(s)

1. **Determine the PR/branch:**
   - If `$ARGUMENTS` is empty: get current branch with `git rev-parse --abbrev-ref HEAD`, then find its open PR
   - If `$ARGUMENTS` is a number: treat as PR number
   - If `$ARGUMENTS` is a URL: extract PR number from it
   - If `$ARGUMENTS` looks like a branch name: use that branch
   - If `$ARGUMENTS` is numeric and large (8+ digits): treat as workflow run ID

2. **Fetch workflow runs for the target:**
   ```bash
   gh run list --branch <branch> --limit 10 --json databaseId,name,status,conclusion,event,headBranch,workflowName
   ```

3. **Identify failing runs and check for workflow chains:**
   - Look for runs with `conclusion: "failure"`
   - Check `event` field for `workflow_run` (indicates this was triggered by another workflow)
   - If chained workflows exist, trace back to find the root trigger
   - Build a chain: [root workflow] → [triggered workflow] → [failing workflow]
   - **Remember this chain** - you'll need to verify the entire chain passes after fixes

4. **Present chain to user:**
   - If multiple workflows are involved in the chain, show the full chain
   - Use AskUserQuestion to ask which workflow(s) to debug
   - If only one failing workflow, proceed with that one
   - **Keep track of the original failing workflow** - after fixes, you must verify this same workflow succeeds when re-triggered

## Phase 2: Analyze Failures

1. **For the selected failing workflow(s):**
   - Download logs: `gh run view <run-id> --log-failed`
   - Identify the failing job and step
   - Parse error messages and stack traces

2. **Categorize the failure:**
   - Build/test issue (can likely reproduce locally)
   - Workflow config issue (need to fix `.github/workflows/*.yml`)
   - Environment/secrets issue (may need user input)
   - Dependency issue (package versions, missing tools, etc.)

## Phase 3: Local Validation

**Before pushing any fix, validate locally when possible:**

1. **Discover local tooling:**
   ```bash
   just -l
   ```
   - Check for nested justfiles: `cd cdk && just -l`, `cd frontend && just -l`, etc.
   - Note which recipes correspond to CI steps

2. **Run equivalent local commands:**
   - Prefer `just <recipe>` over constructing raw commands
   - Match CI steps to local recipes
   - Examples:
     - CI runs `npm test` → run `just test`
     - CI runs `pytest` → run `just test-python`
     - CI runs CDK synth → run `cd cdk && just synth`

3. **Only proceed to push when:**
   - Local validation passes, OR
   - The failure is environment-specific and can't be reproduced locally

## Phase 4: Fix and Push Loop

**Delegate to fix-loop agent** to handle the iterative fix-verify-push cycle.

The fix-loop agent orchestrates an autonomous **two-model loop**:
- **Opus diagnoses** the CI failure and plans fixes
- **Sonnet implements** the planned fixes
- Changes are committed, pushed, and verified in CI
- Repeats until success or blocked

Spawn the `fix-loop` agent with instructions to:

1. **Run the two-model loop:**
   - **Opus (fix-diagnostician)** analyzes the CI logs and produces a structured fix plan
   - **Sonnet (implementation agent)** applies the planned edits with minimal changes
   - The orchestrator (fix-loop) handles verification steps between iterations

2. **Run local validation** before pushing (when possible):
   - Use `just` recipes to test fixes locally (see Phase 3)
   - Only skip local validation if the failure is environment-specific

3. **Commit and push changes:**
   ```bash
   git add <changed-files>
   git commit -m "ci: <brief description of fix>"
   git push
   ```

4. **Poll for workflow completion:**
   - Wait for the new run: `gh run list --branch <branch> --limit 5 --json status,conclusion,name,databaseId,event,workflowName`
   - Wait for `status: "completed"`
   - Check `conclusion`

5. **Follow the chain forward (CRITICAL):**
   - After the immediate workflow completes, **check if it triggers downstream workflows**
   - Look for new workflow runs that were triggered by the workflow that just completed:
     - Check for runs with `event: "workflow_run"`
     - Check for runs with `event: "push"` if a tag/branch was pushed
     - Match by timestamp (runs created shortly after the workflow completed)
   - **Wait for all downstream workflows in the chain to complete**
   - **If any downstream workflow fails, continue the debug loop on that workflow**
   - Example: You fix main workflow → it succeeds → it pushes a tag → triggered build workflow runs → you must wait for the build workflow too

6. **Chain completion verification:**
   - If the original `$ARGUMENTS` was a failing workflow URL from the end of a chain, the loop only succeeds when:
     - The immediate workflow passes, AND
     - All downstream workflows it triggers also pass
   - This ensures the entire chain is fixed, not just the first step

7. **Pass new error logs to Opus for re-diagnosis:**
   - If any workflow in the chain is still failing:
     - Download new logs: `gh run view <new-run-id> --log-failed`
     - Pass to Opus for fresh analysis
     - Opus plans next fix
     - Sonnet applies it
     - Repeat loop

8. **Stop conditions:**
   - **Success:** All workflows in the chain pass (`conclusion: "success"`) → return summary
   - **Blocked:** Cycling through same errors without progress (Opus will identify blockers)
   - **Need input:** Secrets, permissions, architectural decisions → return what's needed

**Expected agent return**: Concise summary of fixes applied and final status, without verbose logs. The fix-loop orchestrator will manage the opus/sonnet cycles internally.

## Workflow Chain Navigation

**When a workflow triggers another workflow:**
- Event type `workflow_run` indicates a chained workflow
- Use `gh run view <id> --json event,workflowName,triggeredBy` to trace relationships
- Example chain:
  - "Release" workflow (pushes a tag)
  - → "Build" workflow (triggered on: push tags)
  - → "Deploy" workflow (triggered by build completion)
- The fix may need to be in the triggering workflow, not the failing one
- **Always show the chain and ask user which to debug**

## Notes

- **Prefer local debugging:** CI minutes cost money, local iteration is free and fast
- **Keep fixes minimal:** Don't refactor, clean up, or "improve" unrelated code
- **Track attempts:** Maintain a running log of what was tried and what changed
- **Bounded retries:** If you're cycling through the same 2-3 errors without progress, stop and report
