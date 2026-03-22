---
name: gws
description: >-
  This skill should be used when the user asks to "use gws", "run a gws command",
  "check my email", "send an email", "reply to an email", "read an email",
  "list my drive files", "upload to drive", "search drive",
  "check my calendar", "what meetings do I have", "create a calendar event",
  "read a spreadsheet", "append to a spreadsheet",
  "list my tasks", "create a task", "standup report", "meeting prep",
  or otherwise interact with Google Workspace services
  (Gmail, Drive, Calendar, Sheets, Tasks, Docs, Slides, etc.)
  via the gws CLI tool.
---

# Google Workspace CLI (gws)

`gws` is a CLI for all Google Workspace APIs. Use it to interact with Gmail, Drive,
Calendar, Sheets, Tasks, and more from the terminal.

## CLI Reference

!`gws --help`

## Command Pattern

```
gws <service> <resource> [sub-resource] <method> [flags]
```

Examples:
```
gws drive files list --params '{"pageSize": 10}'
gws sheets spreadsheets values get --params '{"spreadsheetId": "...", "range": "Sheet1"}'
gws gmail users messages list --params '{"userId": "me", "q": "is:unread"}'
gws schema drive.files.list
```

## Google Docs Convention

**Always represent Google Docs as markdown locally** unless the user specifies otherwise.

- **Pull** a doc: export with `mimeType: text/markdown`
- **Push** a doc: upload with `--upload-content-type text/markdown` and `mimeType: application/vnd.google-apps.document`

Drive handles markdown↔Google Docs conversion automatically. See `references/service-guide.md` for full recipes.

## Helper Commands (Preferred)

Many services expose `+helper` commands with ergonomic named flags. **Always prefer
helpers when available** — they handle MIME encoding, threading, base64, and other
complexity automatically.

Run `gws <service> +<helper> --help` for exact flags and examples.

| Service    | Helper              | Purpose                                          |
|------------|---------------------|--------------------------------------------------|
| gmail      | `+send`             | Send an email                                    |
| gmail      | `+triage`           | Show unread inbox summary (sender, subject, date)|
| gmail      | `+read`             | Read a message body or headers                   |
| gmail      | `+reply`            | Reply to a message (handles threading)           |
| gmail      | `+reply-all`        | Reply-all to a message (handles threading)       |
| gmail      | `+forward`          | Forward a message to new recipients              |
| gmail      | `+watch`            | Watch for new emails, stream as NDJSON           |
| drive      | `+upload`           | Upload a file with automatic metadata            |
| sheets     | `+read`             | Read values from a spreadsheet                   |
| sheets     | `+append`           | Append rows to a spreadsheet                     |
| calendar   | `+insert`           | Create a new calendar event                      |
| calendar   | `+agenda`           | Show upcoming events across all calendars        |
| workflow   | `+standup-report`   | Today's meetings + open tasks as standup summary |
| workflow   | `+meeting-prep`     | Next meeting: agenda, attendees, linked docs     |
| workflow   | `+email-to-task`    | Convert a Gmail message into a Tasks entry       |
| workflow   | `+weekly-digest`    | Weekly summary of meetings and unread email      |
| workflow   | `+file-announce`    | Announce a Drive file in a Chat space            |

Quick examples:
```bash
# Triage inbox
gws gmail +triage --format table

# Send email
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi!'

# Check today's agenda
gws calendar +agenda --today --format table

# Upload a file
gws drive +upload ./report.pdf --parent FOLDER_ID

# Standup summary
gws workflow +standup-report --format table
```

## Raw API Commands

Use raw API calls when no helper exists for the operation.

**Read (GET with query params):**
```bash
gws gmail users messages list --params '{"userId": "me", "q": "from:boss is:unread", "maxResults": 10}'
```

**Write (POST/PATCH with request body):**
```bash
gws tasks tasks insert --params '{"tasklist": "@default"}' --json '{"title": "Follow up on report"}'
```

The `--params` flag takes URL/query parameters as JSON. The `--json` flag takes the
request body as JSON. Run `gws schema <service.resource.method>` to discover what
parameters a method accepts.

## Schema Discovery

Before guessing parameter names, use schema discovery:

```bash
# Discover parameters for a method
gws schema gmail.users.messages.list

# Discover a request/response body type
gws schema gmail.Message

# List resources for a service
gws gmail --help

# List methods for a resource
gws gmail users messages --help
```

Schema output shows parameter names, types, descriptions, and required/optional status.
Use this instead of guessing — it's faster and accurate.

## Core Flags

| Flag                     | Purpose                                          |
|--------------------------|--------------------------------------------------|
| `--params '<JSON>'`      | URL/query parameters                             |
| `--json '<JSON>'`        | Request body (POST/PATCH/PUT)                    |
| `--format <fmt>`         | Output: `json` (default), `table`, `yaml`, `csv`|
| `--upload <path>`        | Upload a local file as media content             |
| `--upload-content-type`  | MIME type override (auto-detected from extension)|
| `--output <path>`        | Save binary response to file                     |
| `--dry-run`              | Validate request locally without sending         |
| `--api-version <ver>`    | Override API version (e.g. `v3`)                 |

## Pagination

For large result sets, use `--page-all` to auto-paginate. Output is NDJSON (one JSON
object per page):

```bash
# Fetch all pages, process with jq
gws drive files list --params '{"pageSize": 100}' --page-all | jq -s '.[].files[]'

# Limit pages fetched
gws drive files list --page-all --page-limit 5

# Add delay between pages to avoid rate limits
gws drive files list --page-all --page-delay 500
```

Default page limit is 10; default delay is 100ms.

## Error Handling

| Exit code | Meaning                          |
|-----------|----------------------------------|
| 0         | Success                          |
| 1         | API error (Google returned error)|
| 2         | Auth error (credentials missing) |
| 3         | Validation error (bad arguments) |
| 4         | Discovery error (API schema)     |
| 5         | Internal error                   |

On exit code 2, run `gws auth login` to re-authenticate.

## Authentication

```bash
# Authenticate (opens browser)
gws auth login

# Limit to specific services (reduces OAuth scope)
gws auth login -s drive,gmail,sheets

# Check current auth state
gws auth status

# Logout
gws auth logout
```

## Additional Resources

For detailed per-service recipes, helper flag reference, and advanced patterns, consult:
- **`references/service-guide.md`** — Per-service command examples for Gmail, Drive,
  Calendar, Sheets, Tasks, and Workflows
