---
description: Address, reply to, and resolve PR review comments
argument-hint: "[thread IDs or 'all']"
allowed-tools: Bash(gh:*), Bash(${CLAUDE_PLUGIN_ROOT}/commands/scripts:*), Read, Edit, Write, Glob, Grep
---

# Reply to PR Review Comments

Address PR review comments by implementing the requested changes, then reply to and resolve their threads.

## Current PR Context

**Current PR GraphQL ID:** !`gh pr view --json id -q '.id'`

**Unresolved review threads:** !`${CLAUDE_PLUGIN_ROOT}/commands/scripts/get-unresolved-threads.sh`

## Workflow

For threads specified in `$ARGUMENTS`:

1. **Identify which threads to process**
   - If `$ARGUMENTS` is missing or "all", process all unresolved threads from context above
   - Otherwise, treat `$ARGUMENTS` as space-separated thread IDs

2. **Plan the implementation**
   - Read each comment to understand what change is requested
   - Use TodoWrite to create a task list for implementing each change
   - Group related changes if multiple comments affect the same area

3. **Implement the changes**
   - For each comment, make the requested code changes
   - Mark todos as completed as you go
   - If a comment is unclear or you disagree with it, use AskUserQuestion to clarify

4. **Reply and resolve each thread**
   After implementing, for each thread:

   a. Write a concise reply explaining what was changed

   b. Execute the combined mutation:
   ```bash
   gh api graphql -f query='
   mutation($threadId: ID!, $body: String!) {
     addPullRequestReviewThreadReply(input: {
       pullRequestReviewThreadId: $threadId,
       body: $body
     }) {
       comment { id }
     }
     resolveReviewThread(input: {
       threadId: $threadId
     }) {
       thread { isResolved }
     }
   }' -f threadId="THREAD_ID" -f body="REPLY_TEXT"
   ```

5. **Confirm completion**
   - List which threads were addressed and resolved
   - Show any errors encountered

## Example Reply Format

Replies should be concise and reference the specific change:

- "Done. Switched to `query(begins_with='ANALYSIS_')` instead of individual gets."
- "Fixed. Added timezone info with `.isoformat(timespec='seconds') + 'Z'`."
- "Addressed. Created `AttachmentRecord` dataclass in `models.py` and updated serialization."

## Error Handling

- If mutation fails, check that the thread ID is correct (starts with `PRRT_`)
- If thread is already resolved, you'll see `isResolved: true` in the response
- Escape special characters in the reply body (especially quotes)

## Notes

- Thread IDs are GraphQL node IDs (format: `PRRT_kwDO...`)
- These are shown in the context section above for unresolved threads
- Both operations execute in a single request for efficiency
- The mutation is atomic - both succeed or both fail
