#!/bin/bash
set -euo pipefail

APP_DIR="/home/ubuntu/HISUB/hisubtory"
VENV_DIR="/home/ubuntu/HISUB/workenv"

echo "[1/3] Ensuring virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[2/3] Activating virtual environment..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "[3/3] Installing Python dependencies..."
pip install --upgrade pip wheel setuptools

# 프로젝트 requirements.txt가 있으면 그걸 우선 사용
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt"
else
  # 최소 실행 패키지 (수업용)
  pip install django gunicorn pymysql python-dotenv pillow
fi

echo "[Install] Done."
