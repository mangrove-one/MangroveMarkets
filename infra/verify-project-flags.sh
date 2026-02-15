#!/usr/bin/env bash
# Verify all gcloud commands in the codebase use --project flag
# This prevents accidental changes to global gcloud configuration

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIRED_PROJECT="mangrove-markets"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Verifying all gcloud commands use --project=${REQUIRED_PROJECT} flag..."
echo

# Files to check
FILES_TO_CHECK=(
    ".github/workflows/deploy-cloudrun.yaml"
    "infra/terraform/terraform.sh"
    "infra/terraform/README.md"
    "infra/terraform/SETUP.md"
    "docs/domain-setup.md"
    "README.md"
)

ISSUES_FOUND=0

for file in "${FILES_TO_CHECK[@]}"; do
    filepath="${PROJECT_ROOT}/${file}"

    if [ ! -f "$filepath" ]; then
        echo -e "${YELLOW}SKIP${NC} ${file} (not found)"
        continue
    fi

    # Find gcloud commands (excluding comments and example explanations)
    gcloud_lines=$(grep -n "gcloud " "$filepath" | grep -v "^[[:space:]]*#" | grep -v "gcloud config" || true)

    if [ -z "$gcloud_lines" ]; then
        echo -e "${GREEN}OK${NC}   ${file} (no gcloud commands)"
        continue
    fi

    # Check each gcloud command for --project flag
    while IFS= read -r line; do
        line_num=$(echo "$line" | cut -d: -f1)
        content=$(echo "$line" | cut -d: -f2-)

        # Skip if this is just a comment or documentation
        if echo "$content" | grep -q "^\s*#\|^\s*-\|^\s*\*"; then
            continue
        fi

        # Skip gcloud commands that don't support --project flag
        if echo "$content" | grep -qE "gcloud (config|auth|init|version)"; then
            continue
        fi

        # Skip if this is just in a comment or quoted string showing what not to do
        if echo "$content" | grep -qE "(Run:|gcloud auth|application-default)"; then
            continue
        fi

        # Check if this line or nearby lines have --project flag
        # Get context (this line and next 15 lines for multi-line commands)
        context=$(sed -n "${line_num},$((line_num + 15))p" "$filepath")

        if ! echo "$context" | grep -q "\-\-project"; then
            echo -e "${RED}FAIL${NC} ${file}:${line_num}"
            echo "      Missing --project flag: ${content}"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    done <<< "$gcloud_lines"

    # If no issues were found for this file
    if [ $ISSUES_FOUND -eq 0 ]; then
        echo -e "${GREEN}OK${NC}   ${file}"
    fi
done

echo
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All gcloud commands properly use --project flag${NC}"
    exit 0
else
    echo -e "${RED}✗ Found ${ISSUES_FOUND} gcloud command(s) missing --project flag${NC}"
    echo
    echo "All gcloud commands must include --project=${REQUIRED_PROJECT} flag"
    echo "This prevents accidental changes to global gcloud configuration."
    exit 1
fi
