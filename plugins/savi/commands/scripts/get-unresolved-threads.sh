#!/bin/bash
# Get unresolved PR review threads with their GraphQL IDs

PR_ID=$(gh pr view --json id -q '.id')

gh api graphql -f query='
query($pr_id: ID!) {
  node(id: $pr_id) {
    ... on PullRequest {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes {
              body
              author { login }
            }
          }
        }
      }
    }
  }
}' -f pr_id="$PR_ID" --jq '
  .data.node.reviewThreads.nodes[]
  | select(.isResolved == false)
  | "Thread ID: \(.id)\nComment: \(.comments.nodes[0].body)\n---"
'
