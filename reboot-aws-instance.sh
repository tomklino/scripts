#!/bin/bash

set -e

# Default regions (can be overridden via AWS_REGIONS environment variable)
DEFAULT_REGIONS=("us-east-1" "eu-central-1")

# Parse arguments
DRY_RUN=false
INSTANCE_PATTERN=""
CUSTOM_REGIONS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --region)
      CUSTOM_REGIONS+=("$2")
      shift 2
      ;;
    *)
      INSTANCE_PATTERN="$1"
      shift
      ;;
  esac
done

# Determine which regions to use (priority: CLI args > env var > defaults)
if [ ${#CUSTOM_REGIONS[@]} -gt 0 ]; then
  REGIONS=("${CUSTOM_REGIONS[@]}")
elif [ -n "$AWS_REGIONS" ]; then
  IFS=',' read -ra REGIONS <<< "$AWS_REGIONS"
else
  REGIONS=("${DEFAULT_REGIONS[@]}")
fi

# Check if instance name pattern is provided
if [ -z "$INSTANCE_PATTERN" ]; then
  echo "Usage: $0 [--dry-run] [--region <region>]... <instance-name-pattern>"
  echo "Example: $0 amexgbt"
  echo "Example: $0 --dry-run amexgbt"
  echo "Example: $0 --region us-west-2 --region eu-west-1 amexgbt"
  echo ""
  echo "Regions can also be set via AWS_REGIONS env var (comma-separated)"
  echo "Default regions: ${DEFAULT_REGIONS[*]}"
  exit 1
fi

# Run describe-instances for each region and combine outputs
output=""
for region in "${REGIONS[@]}"; do
  region_output=$(aws ec2 describe-instances \
    --region "$region" \
    --filters "Name=tag:Name,Values=*${INSTANCE_PATTERN}*" \
    --query "Reservations[*].Instances[*].[InstanceId,Tags[?Key==\`Name\`].Value|[0],State.Name,PrivateIpAddress,PublicIpAddress,\`${region}\`]" \
    --output text | grep -v '^[[:space:]]*$' || true)
  if [ -n "$region_output" ]; then
    if [ -n "$output" ]; then
      output=$(printf "%s\n%s" "$output" "$region_output")
    else
      output="$region_output"
    fi
  fi
done

# Filter any remaining empty lines
output=$(echo "$output" | grep -v '^[[:space:]]*$' || true)

# Count lines in output
if [ -z "$output" ]; then
  line_count=0
else
  line_count=$(echo "$output" | wc -l | tr -d ' ')
fi

if [ "$line_count" -eq 0 ]; then
  echo "No instances found matching the filter"
  exit 1
elif [ "$line_count" -eq 1 ]; then
  # Extract instance ID and region (first and last fields)
  INSTANCE_ID=$(echo "$output" | awk '{print $1}')
  REGION=$(echo "$output" | awk '{print $NF}')
  echo "Found single instance: $INSTANCE_ID in $REGION"
  echo "Rebooting instance..."

  if [ "$DRY_RUN" = true ]; then
    echo "Would run: aws ec2 reboot-instances --region $REGION --instance-ids $INSTANCE_ID"
    echo "Would run: aws ec2 wait instance-status-ok --region $REGION --instance-ids $INSTANCE_ID"
    echo "[DRY RUN] Instance $INSTANCE_ID would be rebooted"
  else
    aws ec2 reboot-instances --region "$REGION" --instance-ids "$INSTANCE_ID"

    echo "Waiting for instance to become available..."
    aws ec2 wait instance-status-ok --region "$REGION" --instance-ids "$INSTANCE_ID"

    echo "Instance $INSTANCE_ID is now ready"
  fi
else
  # Multiple instances found
  echo "Multiple instances found:"
  echo ""

  # Display numbered choices
  i=1
  while IFS=$'\t' read -r instance_id name state private_ip public_ip region; do
    echo "$i) $instance_id - $name ($state) - Private: $private_ip, Public: $public_ip - Region: $region"
    ((i++))
  done <<< "$output"

  echo ""
  read -p "Select instance number to reboot (1-$line_count): " choice

  # Validate choice
  if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "$line_count" ]; then
    echo "Invalid choice"
    exit 1
  fi

  # Extract selected instance ID and region
  selected_line=$(echo "$output" | sed -n "${choice}p")
  INSTANCE_ID=$(echo "$selected_line" | awk '{print $1}')
  REGION=$(echo "$selected_line" | awk '{print $NF}')

  echo "Rebooting instance: $INSTANCE_ID in $REGION"

  if [ "$DRY_RUN" = true ]; then
    echo "Would run: aws ec2 reboot-instances --region $REGION --instance-ids $INSTANCE_ID"
    echo "Would run: aws ec2 wait instance-status-ok --region $REGION --instance-ids $INSTANCE_ID"
    echo "[DRY RUN] Instance $INSTANCE_ID would be rebooted"
  else
    aws ec2 reboot-instances --region "$REGION" --instance-ids "$INSTANCE_ID"

    echo "Waiting for instance to become available..."
    aws ec2 wait instance-status-ok --region "$REGION" --instance-ids "$INSTANCE_ID"

    echo "Instance $INSTANCE_ID is now ready"
  fi
fi
