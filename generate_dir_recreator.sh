#!/bin/bash

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

echo "echo \"\$TARGET_DIR\""
echo ""
echo "RANDOM_NUM=\$RANDOM"
echo "CONTAINER_NAME=main_armis_observability_shipper_\$RANDOM_NUM"
echo ""
echo "docker run -d \\"
echo "    --name \$CONTAINER_NAME \\"
echo "    --memory 6g \\"
echo "    --memory-swap 6g \\"
echo "    --stop-timeout 60 \\"
echo "    -p 12345-12349:12345 \\"
echo "    --add-host host.docker.internal:host-gateway \\"
echo "    -v /etc/armis/root_ca.crt:/etc/agent/root_ca.crt:ro \\"
echo "    -v /proc:/host/proc:ro \\"
echo "    -v /etc/armis/tenant.json:/etc/agent/tenant.json:ro \\"
echo "    -v /sys:/host/sys:ro \\"
echo "    -v /mnt/data/logs/:/logs:ro \\"
echo "    -v /:/rootfs:ro \\"
echo "    -v /var/run/docker.sock:/tmp/docker.sock:ro \\"
echo "    -v /mnt/data/prometheus/observability_shipper/:/etc/agent/data:rw \\"
echo "    -v /mnt/data/prometheus/sensors:/etc/agent/sensors:ro \\"
echo "    -v \"\$TARGET_DIR\":/armis/deploy/services/observability_shipper/config:ro \\"
echo "    -e AGENT_MODE=flow \\"
echo "    -e LOG_LEVEL=info \\"
echo "    -e DESCRIPTION=\"Observability Shipper responsible for shipping observability data to upstreams\" \\"
echo "    -e OWNER=devops-infra \\"
echo "    -e GROUP_OWNER=dev-infra \\"
echo "    -e AGENT_DEPLOY_MODE=docker \\"
echo "    -l com.armis.domain=infra \\"
echo "    -l com.armis.image_type=observability_shipper \\"
echo "    -l com.armis.metrics_scrape_port=12345 \\"
echo "    -w /armis/deploy/services/observability_shipper/config \\"
echo "    --entrypoint /armis/deploy/services/observability_shipper/run.sh \\"
echo "    armis/observability_shipper:distribute"
echo ""
echo "echo \"Container \$CONTAINER_NAME started. Waiting 10 seconds and showing logs...\""
echo "sleep 10"
echo "docker logs \$CONTAINER_NAME"
echo "docker kill \$CONTAINER_NAME"
echo "docker rm \$CONTAINER_NAME"
