---
name: docs
description: >-
  Use this skill when working with documents in ~/docs/, pushing markdown files
  to Google Docs, pulling Google Docs comments, or pairing markdown files with
  Google Docs. Triggered by: "push this doc to Google", "sync with Google Docs",
  "pair this file with a Google Doc", "show comments from Google Docs",
  "list my docs", or any mention of savi-docs.
---

# Documentation System (savi-docs)

A CLI tool (`savi-docs`) manages local markdown files in `~/docs/` and syncs them
with Google Docs. Local markdown is always the source of truth — Google Docs is
a view, not an editor.

## ~/docs/ Structure

```
~/docs/
  repos/<repo-name>/         # repo-specific docs
    reports/                 # epic-loop report files (not committed to git)
    *.md                     # other repo docs
  general/                   # docs not tied to a specific repo
    *.md
```

Documents are stored here instead of inside repos so they:
- Are not committed to git (no noise in repo history)
- Don't appear in repo context when running Claude Code in a project
- Can optionally be synced to Google Docs

## YAML Front Matter

Any markdown file can be paired with a Google Doc via front matter:

```yaml
---
gdoc_id: "1abc123..."
title: "My Document"
---

# Actual markdown content starts here
```

- `gdoc_id`: the Google Doc ID (required for push/pull-comments)
- `title`: document title shown in Google Docs (optional, defaults to filename)

Front matter is **stripped** before pushing — Google Docs never sees it.
The `gdoc_url` is always derived from `gdoc_id` as
`https://docs.google.com/document/d/{gdoc_id}/edit`.

## savi-docs Commands

Run from anywhere; paths to markdown files must be provided.

```bash
# Push markdown to its paired Google Doc (create if not yet paired)
savi-docs push ~/docs/general/my-doc.md

# Explicitly create a new Google Doc (errors if already paired)
savi-docs create ~/docs/general/my-doc.md --title "My Doc" --parent FOLDER_ID

# Fetch and display comments from the paired Google Doc (read-only)
savi-docs pull-comments ~/docs/general/my-doc.md

# List all docs in ~/docs/ with their pairing status
savi-docs list

# Filter to a specific repo's docs
savi-docs list --repo my-repo-name

# Pair an existing file with an existing Google Doc
savi-docs init ~/docs/general/my-doc.md --doc "https://docs.google.com/..."
```

## Workflow Guidelines

- **Always use `push` for create-or-update** — it creates a new doc if unpaired,
  or updates the existing doc if already paired.
- **Never pull and overwrite the local file** — if someone edits the Google Doc,
  use `pull-comments` to see the changes as comments, then apply them locally.
- **Keep repo-specific docs under `~/docs/repos/<repo-name>/`** and general docs
  under `~/docs/general/`.
- **Reports from epic-loop/breakdown** go in `~/docs/repos/<repo-name>/reports/`.
