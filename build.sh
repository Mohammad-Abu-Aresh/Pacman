#!/usr/bin/env bash

set -e

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --onedir \
    --name pacman \
    pac-man.py

cp -r assets dist/pacman/assets
cp config.example.json dist/pacman/config.json

cat > dist/pacman/run-pacman.sh <<'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
exec ./pacman config.json
EOF

chmod +x dist/pacman/run-pacman.sh