#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
gunicorn -w $WORKERS -b 0.0.0.0:5000 app_main:app
