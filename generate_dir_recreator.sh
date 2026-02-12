#!/bin/bash

## Writes a bash script using heredocs to recreate a folder

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>" >&2
    exit 1
fi

SOURCE_DIR="$1"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory '$SOURCE_DIR' does not exist" >&2
    exit 1
fi

SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"
DIR_NAME="$(basename "$SOURCE_DIR")"

echo "#!/bin/bash"
echo ""
echo "set -euo pipefail"
echo ""
echo "TEMP_DIR=\$(mktemp -d)"
echo "TARGET_DIR=\"\$TEMP_DIR/$DIR_NAME\""
echo "mkdir -p \"\$TARGET_DIR\""

find "$SOURCE_DIR" -type d | while read -r dir; do
    rel_path="${dir#$SOURCE_DIR}"
    if [ -n "$rel_path" ]; then
        echo "mkdir -p \"\$TARGET_DIR$rel_path\""
    fi
done

echo ""

find "$SOURCE_DIR" -type f | while read -r file; do
    rel_path="${file#$SOURCE_DIR}"
    echo "cat > \"\$TARGET_DIR$rel_path\" <<'EOF_$(echo "$rel_path" | tr '/' '_' | tr -d '.-')'"
    cat "$file"
    echo "EOF_$(echo "$rel_path" | tr '/' '_' | tr -d '.-')"
    echo ""
done
