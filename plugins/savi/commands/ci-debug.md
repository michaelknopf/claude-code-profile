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

4. **Present chain to user:**
   - If multiple workflows are involved in the chain, show the full chain
   - Use AskUserQuestion to ask which workflow(s) to debug
   - If only one failing workflow, proceed with that one

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

1. **Apply minimal fix** based on diagnosis
   - Don't refactor or improve beyond fixing the immediate issue
   - Keep changes targeted and reversible

2. **Run local validation** (see Phase 3)

3. **Commit and push:**
   ```bash
   git add <changed-files>
   git commit -m "ci: <brief description of fix>"
   git push
   ```

4. **Wait for CI and check results:**
   - Poll for the new run: `gh run list --branch <branch> --limit 5 --json status,conclusion,name,databaseId`
   - Wait for `status: "completed"`
   - Check `conclusion`

5. **If still failing:**
   - Download new logs: `gh run view <new-run-id> --log-failed`
   - Re-analyze with fresh error output
   - Apply next fix
   - Repeat loop

6. **Stop conditions:**
   - All workflows pass (`conclusion: "success"`) → report success and summary
   - Cycling through same errors without progress → stop and report blockers
   - Need user input (secrets, permissions, architectural decisions) → ask via AskUserQuestion

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
