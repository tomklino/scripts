#!/bin/bash
# power-logic.sh - Immediate suspend on lid close
# Managed by install-power-config.py

# 1 = AC, 0 = Battery
ON_AC=$$(cat /sys/class/power_supply/AC/online)
# Count connected screens (excluding internal eDP)
EXT_SCREEN=$$(find /sys/class/drm/*/status -print | xargs grep -h "^connected" | grep -v "eDP" | wc -l)
# 1 = Closed, 0 = Open
LID_CLOSED=$$(grep -q "closed" /proc/acpi/button/lid/*/state && echo 1 || echo 0)

# SUSPEND LOGIC:
# If lid is closed AND conditions are met
if [ "$$LID_CLOSED" -eq 1 ] && ${condition_str}; then
    systemctl suspend
fi
