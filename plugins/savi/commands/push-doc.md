---
description: Push a local markdown file to its paired Google Doc (creates a new doc if not yet paired)
argument-hint: "<file.md>"
---

# /push-doc — Push Document to Google Docs

Push a local markdown file to its paired Google Doc using `savi-docs push`.

## Arguments

**`$ARGUMENTS`**: Path to the markdown file to push

## Workflow

1. Read the file to verify it exists and inspect its front matter
2. Run `savi-docs push $ARGUMENTS`
3. Report the result (created vs updated, with the Google Docs URL)

## Notes

- If the file has no `gdoc_id` in its front matter, a new Google Doc is created
  and the ID is written back into the file automatically
- If already paired, the existing doc's content is replaced with the current markdown
- Front matter (`gdoc_id`, `title`) is stripped before pushing — Google Docs never sees it
- This command never pulls content from Google Docs; local markdown is always the source of truth
