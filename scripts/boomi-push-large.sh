#!/usr/bin/env bash
# boomi-push-large.sh — push a large Boomi component XML via temp file (avoids arg-list-too-long)
# Usage: bash scripts/boomi-push-large.sh <path/to/component.xml>
set -euo pipefail

SKILL_SCRIPTS="C:/Users/manis/.claude/plugins/cache/boomi-companion/bc-integration/1.0.0/skills/boomi-integration/scripts"
source "${SKILL_SCRIPTS}/boomi-common.sh"
load_env
require_env BOOMI_API_URL BOOMI_USERNAME BOOMI_API_TOKEN BOOMI_ACCOUNT_ID
require_tools curl jq

FILE_PATH="${1:?Usage: $0 <component-xml-path>}"
[[ -f "$FILE_PATH" ]] || { echo "ERROR: File not found: $FILE_PATH" >&2; exit 1; }

COMPONENT_NAME=$(xml_attr "name" < "$FILE_PATH" | head -1)
[[ -z "$COMPONENT_NAME" ]] && COMPONENT_NAME=$(basename "$FILE_PATH" .xml)

echo "Pushing component '$COMPONENT_NAME' (large-file mode)..."

# Write prepared XML (blank componentId) to a temp file
TMPFILE=$(mktemp /tmp/boomi-push-XXXXXX.xml)
trap 'rm -f "$TMPFILE"' EXIT

sed 's/componentId="[^"]*"/componentId=""/' "$FILE_PATH" > "$TMPFILE"

# Push via @file to avoid argument list limits
URL="$(build_api_url "Component")"
boomi_api -X POST "$URL" \
  -H "Accept: application/xml" \
  -H "Content-Type: application/xml" \
  --data-binary "@$TMPFILE"

if [[ "$RESPONSE_CODE" != "200" && "$RESPONSE_CODE" != "201" ]]; then
  echo "ERROR: Create failed (HTTP ${RESPONSE_CODE}): ${RESPONSE_BODY}" >&2
  exit 1
fi

# Extract and write back the platform-assigned componentId
COMPONENT_ID=$(echo "$RESPONSE_BODY" | xml_attr "componentId")
if [[ -z "$COMPONENT_ID" ]]; then
  echo "ERROR: No componentId in response" >&2
  exit 1
fi

sedi "s/componentId=\"\"/componentId=\"${COMPONENT_ID}\"/" "$FILE_PATH"
echo "SUCCESS: '$COMPONENT_NAME' created with ID: $COMPONENT_ID"

# Record sync state
SYNC_DIR="$(dirname "$FILE_PATH")/../.sync-state"
mkdir -p "$SYNC_DIR"
SYNC_KEY=$(echo "$FILE_PATH" | sed 's|.*/active-development/||' | tr '/' '_' | sed 's/\.xml$//')
echo "{\"componentId\":\"$COMPONENT_ID\",\"name\":\"$COMPONENT_NAME\",\"file\":\"$FILE_PATH\"}" \
  > "${SYNC_DIR}/${SYNC_KEY}.json"
