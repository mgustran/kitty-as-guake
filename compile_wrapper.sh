#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p "$SCRIPT_DIR/system_dist"
rm -rf "$SCRIPT_DIR/build"
rm -rf "$SCRIPT_DIR/dist/kitty-guake"
rm -rf "$SCRIPT_DIR/kitty-guake.spec"
rm -rf "$SCRIPT_DIR/system_dist/kitty-guake"

#pyinstaller --onedir \
pyinstaller --onefile \
    --hidden-import='gi' \
    --add-data "images_gui:images_gui" \
    --add-data "templates:templates" \
    --add-data "pyproject.toml:." \
    --name kitty-guake main.py

if [ -f "$SCRIPT_DIR/dist/kitty-guake" ]; then
    cp "$SCRIPT_DIR/dist/kitty-guake" "$SCRIPT_DIR/system_dist/kitty-guake"
    chmod +x "$SCRIPT_DIR/system_dist/kitty-guake"
    echo "Build successful: system_dist/kitty-guake"

    rm -rf "$SCRIPT_DIR/build"
    rm -rf "$SCRIPT_DIR/dist/kitty-guake"
    rm -rf "$SCRIPT_DIR/kitty-guake.spec"
else
    echo "Build failed"
    exit 1
fi