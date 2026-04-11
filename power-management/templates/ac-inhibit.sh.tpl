#!/bin/bash
# ac-inhibit.sh - Block idle suspend when on AC power
# Managed by install-power-config.py

while true; do
    if [ "$$(cat /sys/class/power_supply/AC/online)" -eq 1 ]; then
        logger "Connected to AC. Added inhibit"
        # Hold inhibit continuously while on AC
        # Only release when AC is disconnected
        systemd-inhibit --what=idle --why="On AC Power" bash -c '
            while [ "$$(cat /sys/class/power_supply/AC/online)" -eq 1 ]; do
                sleep ${check_interval}
            done
        '
        logger "Disconnected from AC. Inhibit removed"
    else
        sleep ${check_interval}
    fi
done
