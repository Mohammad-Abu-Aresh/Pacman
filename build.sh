#!/usr/bin/env bash

set -e

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --name pacman \
    --collect-all mazegenerator \
    --add-data "config.json:." \
    --add-data "photos" \
    pac-man.py
