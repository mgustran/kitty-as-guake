#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p "$SCRIPT_DIR/system_dist"
rm -rf "$SCRIPT_DIR/build"
rm -rf "$SCRIPT_DIR/dist/kgcli"
rm -rf "$SCRIPT_DIR/kgcli.spec"
rm -rf "$SCRIPT_DIR/system_dist/kgcli"

pyinstaller --onefile --name kgcli --add-data "pyproject.toml:." main_cli.py
#pyinstaller --onedir --name kgcli --add-data "pyproject.toml:." main_cli.py

if [ -f "$SCRIPT_DIR/dist/kgcli" ]; then
    cp "$SCRIPT_DIR/dist/kgcli" "$SCRIPT_DIR/system_dist/kgcli"
    chmod +x "$SCRIPT_DIR/system_dist/kgcli"
    echo "Build successful: system_dist/kgcli"

    rm -rf "$SCRIPT_DIR/build"
    rm -rf "$SCRIPT_DIR/dist/kgcli"
    rm -rf "$SCRIPT_DIR/kgcli.spec"
else
    echo "Build failed"
    exit 1
fi