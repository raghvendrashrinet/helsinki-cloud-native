### 1.API health checks with webhook alerts
##### Option 1: Python Script (Recommended)
```python
import requests
import sys
from datetime import datetime, timezone

# Configuration
API_URL = "https://api.example.com/health"
WEBHOOK_URL = "https://slack.com"
TIMEOUT_SECONDS = 10

def send_webhook_alert(message: str):
    # Compatible with Slack ("text") and Discord ("content")
    payload = {
        "text": message,
        "content": message
    }
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send webhook alert: {e}", file=sys.stderr)

def check_api_health():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        if response.status_code != 200:
            alert_msg = (
                f"🚨 *API Health Check Failed*\n"
                f"• *Endpoint:* {API_URL}\n"
                f"• *Status Code:* {response.status_code}\n"
                f"• *Time:* {timestamp}"
            )
            send_webhook_alert(alert_msg)
            sys.exit(1)
        else:
            print(f"[{timestamp}] OK - {API_URL} returned 200")
    except requests.RequestException as e:
        alert_msg = (
            f"🔥 *API Unreachable*\n"
            f"• *Endpoint:* {API_URL}\n"
            f"• *Error:* {str(e)}\n"
            f"• *Time:* {timestamp}"
        )
        send_webhook_alert(alert_msg)
        sys.exit(1)

if __name__ == "__main__":
    check_api_health()
```
##### Bash Script (Zero Dependencies)
```bash
#!/bin/bash

API_URL="https://api.example.com/health"
WEBHOOK_URL="https://slack.com"
TIMEOUT=10

# Fetch HTTP status code (returns 000 if connection fails/times out)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$API_URL")

if [ "$STATUS" -ne 200 ]; then
    MESSAGE="🚨 API Alert: $API_URL failed with status code $STATUS at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    curl -s -X POST -H "Content-Type: application/json" \
         -d "{\"text\": \"$MESSAGE\", \"content\": \"$MESSAGE\"}" \
         "$WEBHOOK_URL" > /dev/null
    exit 1
fi

echo "OK: $API_URL is healthy (200)"
```
-- make docker file and use cronjob or 
Automating with Cron

To run the check automatically every 5 minutes, open your crontab (crontab -e) and add:
```
*/5 * * * * /usr/bin/python3 /path/to/health_check.py >> /var/log/api_health.log 2>&1
```
---
### 2. Stale files and log directories Cleanup
##### Option 1: Bash Script (Recommended for Linux Servers)
script safely deletes files older than a set number of days, avoids deleting active directories, and removes empty subdirectories left behind.
```bash
#!/bin/bash
set -euo pipefail

# Configuration
TARGET_DIR="/var/log/my_app"
DAYS_OLD=14
FILE_PATTERN="*.log*" # Use "*" to match all files
DRY_RUN=false         # Set to true to preview what will be deleted

# Safety check: Prevent accidentally wiping root or empty paths
if [[ -z "$TARGET_DIR" || "$TARGET_DIR" == "/" ]]; then
    echo "Error: Invalid TARGET_DIR specified." >&2
    exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Directory $TARGET_DIR does not exist." >&2
    exit 1
fi

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting cleanup in $TARGET_DIR (older than $DAYS_OLD days)..."

if [[ "$DRY_RUN" == true ]]; then
    echo "--- DRY RUN MODE (No files will be deleted) ---"
    find "$TARGET_DIR" -type f -name "$FILE_PATTERN" -mtime +"$DAYS_OLD" -print
else
    # Delete matching stale files
    find "$TARGET_DIR" -type f -name "$FILE_PATTERN" -mtime +"$DAYS_OLD" -print -delete
    
    # Remove any empty subdirectories (excluding the root target directory itself)
    find "$TARGET_DIR" -mindepth 1 -type d -empty -delete
fi

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Cleanup complete."
```

##### Option 2: Python Script (Cross-Platform & Granular)
```python 
import os
import time
from pathlib import Path
from datetime import datetime, timezone

# Configuration
TARGET_DIR = Path("/var/log/my_app")
DAYS_OLD = 14
DRY_RUN = False  # Set to True to preview deletions without removing files

def cleanup_stale_files():
    if not TARGET_DIR.exists() or not TARGET_DIR.is_dir():
        print(f"Error: Target directory '{TARGET_DIR}' does not exist.")
        return

    cutoff_time = time.time() - (DAYS_OLD * 86400)
    deleted_files = 0
    freed_bytes = 0

    print(f"[{datetime.now(timezone.utc).isoformat()}] Scanning {TARGET_DIR}...")

    # Walk bottom-up so empty directories can be removed after files are deleted
    for root, dirs, files in os.walk(TARGET_DIR, topdown=False):
        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name
            try:
                stat = file_path.stat()
                if stat.st_mtime < cutoff_time:
                    if DRY_RUN:
                        print(f"[DRY RUN] Would delete: {file_path}")
                    else:
                        file_path.unlink()
                        print(f"Deleted: {file_path}")
                    deleted_files += 1
                    freed_bytes += stat.st_size
            except OSError as e:
                print(f"Skipping {file_path}: {e}")

        # Remove empty subdirectories (skip TARGET_DIR itself)
        if root_path != TARGET_DIR and not any(root_path.iterdir()):
            if DRY_RUN:
                print(f"[DRY RUN] Would remove empty dir: {root_path}")
            else:
                root_path.rmdir()
                print(f"Removed empty dir: {root_path}")

    freed_mb = freed_bytes / (1024 * 1024)
    action = "Would free" if DRY_RUN else "Freed"
    print(f"Summary: {deleted_files} files processed. {action} {freed_mb:.2f} MB.")

if __name__ == "__main__":
    cleanup_stale_files()

```

---
### 3.PostgreSQL backups (pg_dump) with retention cleanup


This script dumps the database in compressed custom format (.dump), verifies that the backup succeeded and is non-empty, and then deletes backups older than your retention window.
```bash
#!/bin/bash
set -euo pipefail

# Configuration
DB_NAME="my_database"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/var/backups/postgres"
RETENTION_DAYS=7

# Optional: Set password via PGPASSWORD or use ~/.pgpass (recommended)
# export PGPASSWORD="your_secure_password"

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting backup for database: $DB_NAME"

# Run pg_dump in custom compressed format (-Fc)
# Use -F p | gzip > file.sql.gz if you prefer plain SQL text
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -F c -b -v -f "$BACKUP_FILE" "$DB_NAME"; then
    # Verify the backup file exists and is not empty (-s)
    if [[ -s "$BACKUP_FILE" ]]; then
        FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup successful: $BACKUP_FILE ($FILE_SIZE)"
        
        # Retention Cleanup: Only runs if the new backup succeeded
        echo "Cleaning up backups older than $RETENTION_DAYS days..."
        find "$BACKUP_DIR" -type f -name "${DB_NAME}_*.dump" -mtime +"$RETENTION_DAYS" -print -delete
    else
        echo "Error: Backup file was created but is empty. Skipping retention cleanup." >&2
        rm -f "$BACKUP_FILE"
        exit 1
    fi
else
    echo "Error: pg_dump failed. Skipping retention cleanup." >&2
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup and retention process completed."
```

---

### 4.API DATA SYNC /REPORT FETCHER
 Python script for fetching data from an API (with pagination, rate-limit handling, and retries) and exporting it to CSV and JSON reports.  
This script handles common real-world API hurdles: automatic retries on server errors (5xx), backoff on rate limits (429), pagination loops, and clean timestamped report generation.
```python
import csv
import json
import time
import sys
from pathlib import Path
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
API_BASE_URL = "https://example.com"
API_TOKEN = "YOUR_API_BEARER_TOKEN"
OUTPUT_DIR = Path("./reports")
PAGE_SIZE = 100
MAX_PAGES = 50  # Safety cap to prevent infinite loops

def create_session() -> requests.Session:
    """Creates a requests session with automatic retry logic."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,  # Waits 2s, 4s, 8s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "DataSyncFetcher/1.0"
    })
    return session

def fetch_all_records(session: requests.Session) -> list[dict]:
    """Fetches paginated records from the API."""
    all_records = []
    page = 1

    while page <= MAX_PAGES:
        params = {"page": page, "limit": PAGE_SIZE}
        print(f"Fetching page {page}...")

        try:
            response = session.get(API_BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)
            sys.exit(1)

        # Adjust key lookup based on your API's JSON structure (e.g., payload["data"] or payload)
        records = payload.get("data", payload) if isinstance(payload, dict) else payload

        if not records:
            break

        all_records.extend(records)

        # Stop if fewer records than PAGE_SIZE were returned (last page)
        if len(records) < PAGE_SIZE:
            break

        page += 1
        time.sleep(0.2)  # Polite pacing to avoid hitting rate limits

    return all_records

def save_reports(records: list[dict]):
    """Saves fetched records to both JSON and CSV formats."""
    if not records:
        print("No records returned from API. Skipping file export.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 1. Save Raw JSON
    json_path = OUTPUT_DIR / f"report_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(records, jf, indent=2, ensure_ascii=False)
    print(f"Saved JSON report: {json_path}")

    # 2. Save Flattened CSV
    csv_path = OUTPUT_DIR / f"report_{timestamp}.csv"
    # Collect all unique keys across records in case fields vary
    fieldnames = list(dict.fromkeys(key for row in records for key in row.keys()))

    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved CSV report:  {csv_path} ({len(records)} rows)")

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting API data sync...")
    session = create_session()
    records = fetch_all_records(session)
    save_reports(records)
    print("Sync completed successfully.")

if __name__ == "__main__":
    main()

```
