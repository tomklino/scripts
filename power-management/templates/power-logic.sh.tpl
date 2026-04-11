#!/bin/bash
# power-logic.sh - Immediate suspend on lid close
# Managed by install-power-config.py

# Configuration (set by installer)
ON_BATTERY_REQUIRED=${on_battery}
NO_EXTERNAL_MONITOR_REQUIRED=${require_no_external_monitor}

# 1 = AC, 0 = Battery
ON_AC=$$(cat /sys/class/power_supply/AC/online)
# Count connected screens (excluding internal eDP)
EXT_SCREEN=$$(find /sys/class/drm/*/status -print | xargs grep -h "^connected" | grep -v "eDP" | wc -l)
# 1 = Open, 0 = Closed
LID_OPEN=$$(grep -q "open" /proc/acpi/button/lid/*/state && echo 1 || echo 0)

# Build suspend condition
SUSPEND="yes"

if [ "$$LID_OPEN" -eq 1 ]; then
    SUSPEND="no"
fi

if [ "$$ON_BATTERY_REQUIRED" = "true" ] && [ "$$ON_AC" -eq 1 ]; then
    SUSPEND="no"
fi

if [ "$$NO_EXTERNAL_MONITOR_REQUIRED" = "true" ] && [ "$$EXT_SCREEN" -ge 1 ]; then
    SUSPEND="no"
fi

if [ "$$SUSPEND" = "yes" ]; then
    systemctl suspend
fi
