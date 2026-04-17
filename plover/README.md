# Installing the plover service

1. Place the plover executable (file ending with `AppImage`) in `/opt`
2. Place the `plover` script in `/opt/plover`
3. Populate the `USER` field in `plover.service` and edit the
   DBUS environment variable to match your user ID
4. Place the service in `/usr/lib/systemd/system/plover.service`
5. Reload systemd services: `sudo systemctl daemon-reload`
6. Enable the service: `sudo systemctl enable plover.service`

