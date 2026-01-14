#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/HISUB/hisubtory"
VENV_DIR="/home/ubuntu/HISUB/workenv"

echo "[Start] Ensuring Gunicorn service..."

if [ ! -f /etc/systemd/system/gunicorn.service ]; then
  echo "[Start] Creating /etc/systemd/system/gunicorn.service"
  sudo tee /etc/systemd/system/gunicorn.service >/dev/null <<EOF
[Unit]
Description=Gunicorn Daemon for Django
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --chdir ${APP_DIR} --workers 3 --bind 0.0.0.0:8000 project.wsgi:application
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
fi

sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn --no-pager
