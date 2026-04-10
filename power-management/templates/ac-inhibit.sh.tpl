#!/bin/bash
# ac-inhibit.sh - Block idle suspend when on AC power
# Managed by install-power-config.py

while true; do
    if [ "$$(cat /sys/class/power_supply/AC/online)" -eq 1 ]; then
        # This command blocks the IdleAction from logind
        systemd-inhibit --what=idle --why="On AC Power" sleep ${check_interval}
    else
        sleep ${check_interval}
    fi
done
