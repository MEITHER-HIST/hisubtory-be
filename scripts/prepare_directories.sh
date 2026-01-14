#!/bin/bash
set -euo pipefail

# 배포 폴더
BASE_DIR="/home/ubuntu/HISUB"
APP_DIR="${BASE_DIR}/hisubtory"

echo "[BeforeInstall] Preparing directories..."
echo "  BASE_DIR=${BASE_DIR}"
echo "  APP_DIR=${APP_DIR}"

# BASE_DIR 생성
if [ ! -d "$BASE_DIR" ]; then
  echo "- Creating base directory: $BASE_DIR"
  sudo mkdir -p "$BASE_DIR"
  sudo chown ubuntu:ubuntu "$BASE_DIR"
fi

# APP_DIR 생성
if [ ! -d "$APP_DIR" ]; then
  echo "- Creating app directory: $APP_DIR"
  sudo mkdir -p "$APP_DIR"
  sudo chown -R ubuntu:ubuntu "$APP_DIR"
fi

# 권한 정리
sudo chown -R ubuntu:ubuntu "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"

echo "[BeforeInstall] Directory preparation complete."
