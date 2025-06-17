#!/usr/bin/env bash
set -e
pip install -r requirements.txt    # Install dependencies
pip install -e .                   # Install your package in editable mode
