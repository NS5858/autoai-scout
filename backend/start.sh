#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "🚀 Starting AutoAI Backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir app
