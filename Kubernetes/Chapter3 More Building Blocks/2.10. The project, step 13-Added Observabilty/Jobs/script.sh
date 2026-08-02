#!/bin/sh

# 1. Fetch location header from Wikipedia random endpoint
REDIRECT_URL=$(curl -sI "https://en.wikipedia.org/wiki/Special:Random" | grep -i "^location:" | awk '{print $2}' | tr -d '\r')

if [ -z "$REDIRECT_URL" ]; then
  echo "Failed to fetch random article"
  exit 1
fi

# 2. Check if the URL is relative (/wiki/...) or already absolute (https://...)
if echo "$REDIRECT_URL" | grep -q "^/"; then
  FULL_URL="https://en.wikipedia.org$REDIRECT_URL"
else
  FULL_URL="$REDIRECT_URL"
fi

TODO_TEXT="Read $FULL_URL"

# 3. Send payload matching backend.py (using "content")
curl -X POST "http://todo-backend-svc:2345/todos" \
     -H "Content-Type: application/json" \
     -d "{\"content\": \"$TODO_TEXT\"}"

echo "Posted todo: $TODO_TEXT"