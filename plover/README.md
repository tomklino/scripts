# Installing the plover service

1. Make a dir `/opt/plover.d/
2. Place the plover executable (file ending with `AppImage`) in `/opt/plover.d`
3. Place the `plover` and `plover-prep.sh` scripts in `/opt/plover.d`
4. Populate the `USER` field in `plover.service` and edit the
   DBUS environment variable to match your user ID
5. Place the service in `/usr/lib/systemd/system/plover.service`
6. Reload systemd services: `sudo systemctl daemon-reload`
7. Enable the service: `sudo systemctl enable plover.service`

