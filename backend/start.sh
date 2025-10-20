#!/usr/bin/env bash
pip install -r requirements.txt
playwright install chromium
uvicorn backend.main:app --host 0.0.0.0 --port 10000

