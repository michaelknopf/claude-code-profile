---
description: Upgrade GitHub Actions versions across all repos in a directory
argument-hint: "[directory]"
allowed-tools: Bash(gh:*), Bash(git:*), Bash(find:*), Read, Edit, Write, Glob, Grep, Agent, WebSearch, AskUserQuestion
---

# /gha-upgrade — Upgrade GitHub Actions across repos

**Target directory:** `$ARGUMENTS` (defaults to `../`)

## Phase 1: Discovery

### 1.1 Resolve target directory

Use the provided argument as the target directory, defaulting to `../` relative to the current directory if none is given.

### 1.2 Find repos

List all subdirectories in the target directory. For each, check if `.github/workflows/` exists. Collect all repos that have workflows.

### 1.3 Apply ignore list

Check for `.unmaintained-repos` in the target directory. If it exists, read it:
- Skip blank lines and lines starting with `#`
- Each remaining line is a repo name to exclude from scanning

Report the final list of repos to be scanned, and which were excluded.

---

## Phase 2: Scan & Detect

For each repo in the scan list, grep all files under `.github/` for `uses:` directives. Extract the action name and version tag from each match.

Build a combined inventory across all repos:

```
action-name@version  →  [list of repos using it]
```

### 2.1 Categorize actions

Separate the inventory into:
- **Internal actions:** Hosted in a repo within the same org (same parent directory as the target directory). Check the source repo's git tags to determine current floating-tag behavior (e.g., does a `v2.0` tag exist that floats?).
- **Public actions:** From external orgs (e.g., `actions/`, `aws-actions/`, `docker/`, etc.). Use WebSearch to look up each action's latest release on GitHub.

For internal actions with floating tags: note which consumers reference an outdated major/minor and therefore need a manual bump vs. which already reference the current floating tag and will auto-update after merge.

---

## Phase 3: Plan

Present a summary table to the user:

```
| Action                              | Current Version(s)     | Latest  | Repos Needing Manual Change |
|-------------------------------------|------------------------|---------|------------------------------|
| actions/checkout                    | @v4, @v5               | @v6     | repo-a, repo-b               |
| my-org/github-actions (setup-just)  | @v1.2, @v2.0 (float)  | @v2.0   | repo-c (v1.2 → manual bump)  |
...
```

Also present:
- **Proposed execution order:** Internal/shared repos first (they publish new tags), then leaf repos in batches
- **Breaking changes detected** (e.g., removed inputs, renamed parameters)
- For each breaking change: which repos are affected and what specific changes are needed

Use AskUserQuestion to confirm the plan before proceeding. Do not execute Phase 4 until the user approves.

---

## Phase 4: Execute (per-repo loop)

Work through repos in dependency order (internal repos before leaf repos). For each repo:

### 4.1 Branch

```bash
cd <repo-dir>
git checkout main && git pull
git checkout -b chore/upgrade-github-actions
```

### 4.2 Apply changes

For each workflow file needing changes:
- Use Read to view the file
- Use Edit to apply version bumps (find-and-replace on `uses:` lines)
- Handle breaking changes: remove deleted inputs, update renamed parameters, adjust defaults that changed (e.g., `persist-credentials`)

Keep changes minimal — only update the `uses:` version references and required breaking-change adaptations. Do not reformat or clean up unrelated content.

### 4.3 Commit and push

```bash
git add .github/
git commit -m "chore: upgrade GitHub Actions versions"
git push -u origin chore/upgrade-github-actions
```

### 4.4 Create PR

```bash
gh pr create \
  --title "chore: upgrade GitHub Actions versions" \
  --body "Upgrades GitHub Actions to latest versions.

Changes:
$(list the specific version bumps for this repo)"
```

### 4.5 Wait for CI

Poll until CI completes:
```bash
gh run list --branch chore/upgrade-github-actions --limit 10 --json databaseId,name,status,conclusion,workflowName
```

Wait until `status: "completed"` for all runs. If any has `conclusion: "failure"`, stop and report the error — do not merge a failing PR. Ask the user how to proceed.

### 4.6 Merge (unless excluded)

When all checks pass:
```bash
gh pr merge <pr-number> --squash --delete-branch
```

Do NOT use `--auto`. Poll manually and merge only after checks pass.

**Never merge repos that are explicitly flagged "PR only — do not merge."**

### 4.7 Wait for post-merge workflows (internal repos only)

For internal repos that publish tags (e.g., via a `tag.yml` workflow):

1. Wait for the `tag.yml` workflow to complete on `main`:
   ```bash
   gh run list --branch main --limit 5 --json databaseId,name,status,conclusion,workflowName
   ```

2. After tagging, verify the floating tag moved:
   ```bash
   git fetch --tags
   git tag -l "v<major>.<minor>" --sort=-version:refname | head -3
   ```
   The floating tag (e.g., `v2.0`) should point to the new commit.

3. Only proceed to the next repo after the floating tag is confirmed up to date.

**Rationale:** Downstream repos reference floating tags like `github-actions@v2.0`. If the floating tag hasn't moved yet, the downstream changes would pull stale action code.

### 4.8 Check for downstream simplifications

After an internal repo's floating tag moves, check whether any downstream repos now reference the correct floating tag automatically — reducing the set of manual changes needed for those repos.

---

## Phase 5: Summary

After all repos are processed, report:

```
GitHub Actions Upgrade Summary
==============================

Repos Updated:
- repo-name: PR #123 — merged ✓
  - actions/checkout: @v5 → @v6
  - actions/upload-artifact: @v4 → @v6

Repos with PRs (not merged):
- repo-name: PR #456 — CI passing, awaiting manual merge

Failures:
- repo-name: CI failed on PR #789
  Error: <brief description>

Actions Upgraded:
- actions/checkout:              @v4/@v5 → @v6
- actions/upload-artifact:       @v4/@v5 → @v6
...

Total: N repos updated, M PRs created, K failures
```

---

## Important Constraints

- **Never write directly to `main`.** Always use a feature branch + PR.
- **Never merge if CI is failing.** Report the failure and stop.
- **Never use `gh pr merge --auto`** — poll and merge manually.
- **Never run AWS write operations** without explicit user permission.
- **Minimize changes:** Only update `uses:` version pins and breaking-change adaptations. Do not reformat, add comments, or modify unrelated lines.
- **Breaking changes require care:** Read the action's changelog or release notes (via WebSearch) before applying breaking-change fixes to confirm the correct adaptation.
