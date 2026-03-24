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
- **Pageless mode**: always set pageless mode on new docs; also set it on existing docs when requested. Use a `docs documents batchUpdate` after create/update:
  ```bash
  gws docs documents batchUpdate \
    --params '{"documentId": "DOC_ID"}' \
    --json '{"requests": [{"updateDocumentStyle": {"documentStyle": {"documentFormat": {"documentMode": "PAGELESS"}}, "fields": "documentFormat"}}]}'
  ```
- **Shared drives**: always include `"supportsAllDrives": true` in `--params` for any Drive operation on a file in a shared drive or shared folder — without it the API returns 404 even if you have access
- **Pull comments**: use `drive comments list` with `fields` to get comment threads with quoted context and replies

Drive handles markdown↔Google Docs conversion automatically.

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

## Service Guide

Per-service command recipes and advanced patterns.

---

## Gmail

### Helpers

**`+send` — Send an email**
```bash
# Simple email
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi Alice!'

# With CC/BCC
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi!' --cc bob@example.com --bcc carol@example.com

# HTML email
gws gmail +send --to alice@example.com --subject 'Report' --body '<b>See attached</b>' --html

# With attachment (can be specified multiple times, 25MB total limit)
gws gmail +send --to alice@example.com --subject 'Report' --body 'See attached' -a report.pdf -a data.csv

# From a send-as alias
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi!' --from alias@example.com
```

**`+triage` — Show unread inbox summary**
```bash
# Default: 20 most recent unread
gws gmail +triage

# Custom query and count
gws gmail +triage --max 5 --query 'from:boss'

# Table format with labels
gws gmail +triage --format table --labels

# Extract subjects via jq
gws gmail +triage --format json | jq '.[].subject'
```

**`+read` — Read a message body**
```bash
# Read plain text body
gws gmail +read --id MSG_ID

# Include From/To/Subject/Date headers
gws gmail +read --id MSG_ID --headers

# Read HTML body
gws gmail +read --id MSG_ID --html

# Extract body via jq
gws gmail +read --id MSG_ID --format json | jq '.body'
```
Note: Handles multipart/alternative, base64 decoding, and HTML-to-text conversion automatically.

**`+reply` — Reply to a message**
```bash
# Simple reply
gws gmail +reply --message-id MSG_ID --body 'Thanks, got it!'

# Add CC
gws gmail +reply --message-id MSG_ID --body 'Looping in Carol' --cc carol@example.com

# Add extra recipient to To field
gws gmail +reply --message-id MSG_ID --body 'Adding Dave' --to dave@example.com

# HTML reply with attachment
gws gmail +reply --message-id MSG_ID --body '<b>Updated version</b>' --html -a updated.docx
```
Note: Automatically sets In-Reply-To, References, and threadId. Quotes original message.

**`+reply-all` — Reply-all**
Same flags as `+reply`. Automatically includes all original recipients.

**`+forward` — Forward a message**
```bash
gws gmail +forward --message-id MSG_ID --to dave@example.com

# With a note above the forwarded message
gws gmail +forward --message-id MSG_ID --to dave@example.com --body 'FYI see below'

# With extra CC
gws gmail +forward --message-id MSG_ID --to dave@example.com --cc eve@example.com
```

**`+watch` — Stream new emails as NDJSON**
```bash
gws gmail +watch
```
Streams incoming messages until interrupted. Useful for real-time monitoring.

### Raw API

`userId` is almost always `"me"` (the authenticated user).

```bash
# List messages with a query
gws gmail users messages list --params '{"userId": "me", "q": "from:boss is:unread", "maxResults": 10}'

# Get a specific message (metadata format — fast)
gws gmail users messages get --params '{"userId": "me", "id": "MSG_ID", "format": "metadata"}'

# Get full message
gws gmail users messages get --params '{"userId": "me", "id": "MSG_ID", "format": "full"}'

# List labels
gws gmail users labels list --params '{"userId": "me"}'

# Mark message as read
gws gmail users messages modify --params '{"userId": "me", "id": "MSG_ID"}' \
  --json '{"removeLabelIds": ["UNREAD"]}'

# Move to trash
gws gmail users messages trash --params '{"userId": "me", "id": "MSG_ID"}'
```

---

## Drive

### Helpers

**`+upload` — Upload a file**
```bash
# Simple upload (MIME type auto-detected)
gws drive +upload ./report.pdf

# Upload to a specific folder
gws drive +upload ./report.pdf --parent FOLDER_ID

# Upload with a different filename
gws drive +upload ./data.csv --name 'Sales Data Q4.csv'
```

### Shared Drives

Any Drive operation on a file in a shared drive or shared folder requires `"supportsAllDrives": true` in `--params`. Without it the API returns 404 even if you have access.

```bash
# Get a file in a shared drive
gws drive files get --params '{"fileId": "FILE_ID", "supportsAllDrives": true, "fields": "id,name,size,mimeType,webViewLink"}'

# Update a file in a shared drive
gws drive files update \
  --params '{"fileId": "FILE_ID", "supportsAllDrives": true}' \
  --upload ./doc.md \
  --upload-content-type text/markdown
```

### Raw API

```bash
# List files (10 most recent)
gws drive files list --params '{"pageSize": 10}'

# Search by name
gws drive files list --params '{"q": "name contains '\''report'\''", "pageSize": 20}'

# Search by type and name
gws drive files list --params '{"q": "mimeType='\''application/pdf'\'' and name contains '\''invoice'\''", "fields": "files(id,name,createdTime)"}'

# Get file metadata
gws drive files get --params '{"fileId": "FILE_ID", "fields": "id,name,size,mimeType,webViewLink"}'

# Download file content
gws drive files get --params '{"fileId": "FILE_ID", "alt": "media"}' --output ./downloaded.pdf

# Create a folder
gws drive files create --json '{"name": "New Folder", "mimeType": "application/vnd.google-apps.folder"}'

# Create a folder inside another folder
gws drive files create --json '{"name": "Sub Folder", "mimeType": "application/vnd.google-apps.folder", "parents": ["PARENT_FOLDER_ID"]}'

# List files in a specific folder
gws drive files list --params '{"q": "'\''FOLDER_ID'\'' in parents"}'

# List shared drives
gws drive drives list

# Delete a file (moves to trash)
gws drive files delete --params '{"fileId": "FILE_ID"}'
```

**Drive `q` query syntax quick reference:**
- `name contains 'text'` — filename contains text
- `name = 'exact name'` — exact filename match
- `mimeType = 'application/pdf'` — by MIME type
- `'FOLDER_ID' in parents` — files in a folder
- `trashed = false` — exclude trash
- Combine with `and`/`or`

---

## Google Docs

The Drive API handles Google Docs. Local representation is **always markdown** by default.

### Pull (Google Doc → local markdown)

```bash
gws drive files export \
  --params '{"fileId": "DOC_ID", "mimeType": "text/markdown"}' \
  --output ./doc.md
```

### Push — create a new Google Doc from markdown

New docs must always be set to pageless mode after creation.

```bash
# Step 1: Create the doc with markdown content
DOC_ID=$(gws drive files create \
  --json '{"name": "My Document", "mimeType": "application/vnd.google-apps.document"}' \
  --upload ./doc.md \
  --upload-content-type text/markdown \
  | jq -r '.id')

# Step 2: Set pageless mode
gws docs documents batchUpdate \
  --params "{\"documentId\": \"$DOC_ID\"}" \
  --json '{"requests": [{"updateDocumentStyle": {"documentStyle": {"documentFormat": {"documentMode": "PAGELESS"}}, "fields": "documentFormat"}}]}'
```

### Push — update an existing Google Doc from markdown

```bash
# Standard update
gws drive files update \
  --params '{"fileId": "DOC_ID"}' \
  --upload ./doc.md \
  --upload-content-type text/markdown

# File in a shared drive (requires supportsAllDrives)
gws drive files update \
  --params '{"fileId": "DOC_ID", "supportsAllDrives": true}' \
  --upload ./doc.md \
  --upload-content-type text/markdown
```

The `--upload-content-type text/markdown` flag tells Drive the source format; Drive auto-converts to Google Docs rich text format.

To set pageless mode on an existing doc (run after the update above):

```bash
gws docs documents batchUpdate \
  --params '{"documentId": "DOC_ID"}' \
  --json '{"requests": [{"updateDocumentStyle": {"documentStyle": {"documentFormat": {"documentMode": "PAGELESS"}}, "fields": "documentFormat"}}]}'
```

### Pull comments

Fetch all comment threads with quoted context and replies. The `fields` parameter is required by the API.

```bash
gws drive comments list \
  --params '{"fileId": "DOC_ID", "pageSize": 100, "fields": "comments(id,content,quotedFileContent,author(displayName),resolved,replies(content,author(displayName)))"}' \
  --page-all
```

- `quotedFileContent` — the document text the comment is anchored to
- `replies` — threaded responses to the comment
- `resolved` — whether the thread has been resolved

### Limitations: multi-tab docs

Drive's markdown→rich text conversion only writes to the **first tab**. The Docs API can target other tabs via `tabId`, but only accepts plain text — there is no way to push markdown as formatted rich text into a non-first tab.

**Do not attempt to create multi-tab docs when converting from markdown.** If you need multiple sections, create separate Google Docs instead.

---

## Calendar

### Helpers

**`+insert` — Create a new event**
```bash
# Basic event (times in RFC3339/ISO 8601)
gws calendar +insert --summary 'Standup' \
  --start '2026-06-17T09:00:00-07:00' \
  --end '2026-06-17T09:30:00-07:00'

# With attendees
gws calendar +insert --summary 'Review' \
  --start '2026-06-17T14:00:00-07:00' \
  --end '2026-06-17T15:00:00-07:00' \
  --attendee alice@example.com \
  --attendee bob@example.com

# With Google Meet link
gws calendar +insert --summary 'Team Sync' \
  --start '2026-06-17T10:00:00-07:00' \
  --end '2026-06-17T10:30:00-07:00' \
  --meet

# With location and description
gws calendar +insert --summary 'Lunch' \
  --start '2026-06-17T12:00:00-07:00' \
  --end '2026-06-17T13:00:00-07:00' \
  --location 'Conference Room B' \
  --description 'Q2 planning lunch'

# On a specific calendar
gws calendar +insert --calendar CALENDAR_ID --summary 'Event' \
  --start '...' --end '...'
```

**`+agenda` — Show upcoming events**
```bash
# Next upcoming events (default)
gws calendar +agenda

# Today only
gws calendar +agenda --today

# Tomorrow
gws calendar +agenda --tomorrow

# This week
gws calendar +agenda --week --format table

# Next N days
gws calendar +agenda --days 3

# Filter to a specific calendar
gws calendar +agenda --today --calendar 'Work'

# With timezone override
gws calendar +agenda --today --timezone America/New_York
```

### Raw API

`calendarId` is `"primary"` for the user's default calendar.

```bash
# List upcoming events
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-06-17T00:00:00Z", "singleEvents": true, "orderBy": "startTime"}'

# Get a specific event
gws calendar events get --params '{"calendarId": "primary", "eventId": "EVENT_ID"}'

# Update an event
gws calendar events patch --params '{"calendarId": "primary", "eventId": "EVENT_ID"}' \
  --json '{"summary": "Updated Title", "location": "Room A"}'

# Delete an event
gws calendar events delete --params '{"calendarId": "primary", "eventId": "EVENT_ID"}'

# List all calendars the user has access to
gws calendar calendarList list
```

---

## Sheets

### Helpers

**`+read` — Read values from a spreadsheet**
```bash
# Read a specific range
gws sheets +read --spreadsheet SPREADSHEET_ID --range 'Sheet1!A1:D10'

# Read an entire sheet
gws sheets +read --spreadsheet SPREADSHEET_ID --range Sheet1

# Table format
gws sheets +read --spreadsheet SPREADSHEET_ID --range 'Sheet1!A1:D10' --format table
```

**`+append` — Append rows to a spreadsheet**
```bash
# Append a single row (comma-separated values)
gws sheets +append --spreadsheet SPREADSHEET_ID --values 'Alice,100,true'

# Append multiple rows at once (JSON array of arrays)
gws sheets +append --spreadsheet SPREADSHEET_ID --json-values '[["Alice","100","true"],["Bob","200","false"]]'
```

### Raw API

The spreadsheetId is found in the Google Sheets URL.

```bash
# Get spreadsheet metadata (sheet names, etc.)
gws sheets spreadsheets get --params '{"spreadsheetId": "SPREADSHEET_ID"}'

# Read a specific range
gws sheets spreadsheets values get --params '{"spreadsheetId": "SPREADSHEET_ID", "range": "Sheet1!A1:C10"}'

# Write values to a range
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "SPREADSHEET_ID", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Name", "Score"], ["Alice", 100]]}'

# Batch read multiple ranges
gws sheets spreadsheets values batchGet \
  --params '{"spreadsheetId": "SPREADSHEET_ID", "ranges": ["Sheet1!A1:B5", "Sheet2!A1:C3"]}'
```

---

## Tasks

No helpers exist for Tasks — use the raw API.

```bash
# List all task lists
gws tasks tasklists list

# List tasks in the default task list
gws tasks tasks list --params '{"tasklist": "@default"}'

# List tasks in a specific task list
gws tasks tasks list --params '{"tasklist": "TASKLIST_ID", "showCompleted": false}'

# Create a task
gws tasks tasks insert --params '{"tasklist": "@default"}' \
  --json '{"title": "Follow up with client", "notes": "Re: Q3 proposal"}'

# Create a task with a due date (RFC3339)
gws tasks tasks insert --params '{"tasklist": "@default"}' \
  --json '{"title": "Submit report", "due": "2026-06-20T00:00:00Z"}'

# Complete a task
gws tasks tasks patch --params '{"tasklist": "@default", "task": "TASK_ID"}' \
  --json '{"status": "completed"}'

# Delete a task
gws tasks tasks delete --params '{"tasklist": "@default", "task": "TASK_ID"}'
```

---

## Workflows

Cross-service productivity helpers that combine multiple APIs in one command.

**`+standup-report` — Today's meetings + open tasks**
```bash
gws workflow +standup-report
gws workflow +standup-report --format table
```

**`+meeting-prep` — Next meeting details**
```bash
# Default calendar
gws workflow +meeting-prep

# Specific calendar
gws workflow +meeting-prep --calendar Work
```
Shows the next upcoming event: attendees, description, linked Drive docs.

**`+email-to-task` — Convert email to task**
```bash
gws workflow +email-to-task --message-id MSG_ID

# Into a specific task list
gws workflow +email-to-task --message-id MSG_ID --tasklist TASKLIST_ID
```
Reads subject as task title and snippet as notes. **Confirm with user before executing.**

**`+weekly-digest` — Weekly summary**
```bash
gws workflow +weekly-digest
```
This week's meetings and unread email count.

**`+file-announce` — Announce a Drive file in Chat**
```bash
gws workflow +file-announce --file FILE_ID --space SPACE_ID
```

---

## Advanced Patterns

### Chaining Commands with jq

Extract message IDs from triage, then read each:
```bash
# Get IDs of unread messages from a sender
IDS=$(gws gmail users messages list \
  --params '{"userId": "me", "q": "from:boss is:unread", "maxResults": 5}' \
  | jq -r '.messages[].id')

# Read each
for id in $IDS; do
  gws gmail +read --id "$id" --headers
  echo "---"
done
```

Extract file IDs and download:
```bash
gws drive files list --params '{"q": "name contains '\''report'\''"}'  \
  | jq -r '.files[] | "\(.id) \(.name)"'
```

### Pagination for Large Result Sets

Collect all files across all pages, then process:
```bash
# Fetch all pages into a file (NDJSON: one page per line)
gws drive files list --params '{"pageSize": 100}' --page-all > pages.ndjson

# Flatten all pages into a single array of files
jq -s '[.[].files[]]' pages.ndjson

# Count total
jq -s '[.[].files[]] | length' pages.ndjson
```

Paginate email search:
```bash
gws gmail users messages list \
  --params '{"userId": "me", "q": "is:unread", "maxResults": 100}' \
  --page-all --page-limit 5 \
  | jq -s '[.[].messages[]] | length'
```
