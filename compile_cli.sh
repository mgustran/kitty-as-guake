#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/system_dist
rm -rf $SCRIPT_DIR/build
rm -rf $SCRIPT_DIR/dist/kgcli
rm -rf $SCRIPT_DIR/system_dist/kgcli

pyinstaller --onefile --name kgcli main_cli.py

# todo:remove
cp -R $SCRIPT_DIR/dist/kgcli $SCRIPT_DIR/system_dist/kgcli
chmod +x $SCRIPT_DIR/system_dist/kgcli