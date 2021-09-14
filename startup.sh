#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
uvicorn main:app --workers $WORKERS --port 5000
