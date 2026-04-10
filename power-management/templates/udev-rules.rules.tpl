# Power management udev rules
# Managed by install-power-config.py

SUBSYSTEM=="power_supply", ACTION=="change", RUN+="/usr/local/bin/power-logic.sh"
SUBSYSTEM=="button", ACTION=="change", KERNEL=="lid*", RUN+="/usr/local/bin/power-logic.sh"
