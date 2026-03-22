# gws Service Guide

Detailed command recipes for each Google Workspace service. Use this alongside
the SKILL.md quick reference when you need exact flag syntax or common API patterns.

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

```bash
gws drive files create \
  --json '{"name": "My Document", "mimeType": "application/vnd.google-apps.document"}' \
  --upload ./doc.md \
  --upload-content-type text/markdown
```

### Push — update an existing Google Doc from markdown

```bash
gws drive files update \
  --params '{"fileId": "DOC_ID"}' \
  --upload ./doc.md \
  --upload-content-type text/markdown
```

The `--upload-content-type text/markdown` flag tells Drive the source format; setting `mimeType: application/vnd.google-apps.document` in the body triggers conversion to Google Docs rich text format.

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
