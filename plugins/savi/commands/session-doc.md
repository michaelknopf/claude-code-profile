---
description: Generate a structured document summarizing the current session for future reference
argument-hint: "[output directory]"
---

# /session-doc — Export Session as Documentation

Generate a comprehensive markdown document that captures the essence of this session.

## Arguments

**`$ARGUMENTS`**: Optional directory path where the document should be created

- If provided: Create the document in the specified directory with an auto-generated filename
- If not provided: Create in the current working directory with an auto-generated filename

**Filename generation**: Always generate a descriptive filename based on the session content, using the pattern:
`session-YYYY-MM-DD-<descriptive-topic-slug>.md`

Examples:
- `/session-doc` → `./session-2025-12-31-claude-code-plugin-development.md`
- `/session-doc ~/Documents/sessions` → `~/Documents/sessions/session-2025-12-31-implementing-auth-system.md`

## Output Requirements

**Format**: A paper-like document, NOT a transcript. Organize by topic, not chronologically.

**Fair Coverage**: Weight all parts of the conversation fairly. Don't overweight recent exchanges.

**Audience**: Another Claude Code session that needs to understand the context and continue the work.

## Document Structure

Organize the document with these sections (adapt as appropriate to content):

### 1. Overview
- One paragraph summarizing the main topic/goal of the session
- Key context the reader needs to understand the discussion

### 2. Problem/Background
- What problem or need prompted this session
- Relevant context, constraints, or prior work

### 3. Key Decisions & Rationale
- Important decisions made during the session
- The reasoning behind each decision
- Alternatives considered and why they were rejected

### 4. Technical Details
- Implementation specifics discussed
- Architecture or design patterns chosen
- Code snippets or file paths relevant to the work

### 5. Open Questions & Next Steps
- Unresolved questions or areas needing further investigation
- Planned follow-up work
- Dependencies or blockers

### 6. Files & References
- Files created, modified, or referenced
- External resources consulted
- Related documentation

## Output Instructions

1. Analyze the ENTIRE conversation, not just recent messages
2. Extract key themes, decisions, and technical details
3. Generate a descriptive topic slug for the filename
4. Determine the output path based on `$ARGUMENTS`
5. Reorganize content into the logical structure above
6. Write in clear, technical prose (not bullet points unless appropriate)
7. Write the document to the generated file path
8. Confirm the full path where the document was saved

## Example Output Style

Write like technical documentation:

> "The session focused on implementing a conversation export feature for Claude Code. After evaluating hooks, skills, and slash commands, the slash command approach was selected because it provides explicit user control over when documents are generated..."

NOT like a transcript:

> ~~"First the user asked about X, then Claude suggested Y..."~~
