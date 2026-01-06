#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/HISUB/hisubtory"
LOG_DIR="/var/log/gunicorn"
LOG_FILE="${LOG_DIR}/gunicorn.log"

echo "[BeforeAllowTraffic] Fixing ownership and permissions..."

# 앱 소유권 (ubuntu로)
sudo chown -R ubuntu:ubuntu "$APP_DIR"
sudo find "$APP_DIR" -type d -exec chmod 755 {} \;
sudo find "$APP_DIR" -type f -exec chmod 644 {} \;

# 로그 디렉터리/파일 준비
sudo mkdir -p "$LOG_DIR"
sudo touch "$LOG_FILE"
sudo chown -R ubuntu:www-data "$LOG_DIR"
sudo chmod 775 "$LOG_DIR"
sudo chmod 664 "$LOG_FILE"

echo "[BeforeAllowTraffic] Permission fix completed."
