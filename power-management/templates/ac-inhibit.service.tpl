[Unit]
Description=Inhibit Suspend on AC Power
After=multi-user.target

[Service]
ExecStart=/usr/local/bin/ac-inhibit.sh
Restart=always

[Install]
WantedBy=multi-user.target
