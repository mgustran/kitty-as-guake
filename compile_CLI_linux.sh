#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/system_dist
rm -rf $SCRIPT_DIR/build
rm -rf $SCRIPT_DIR/dist
rm -rf $SCRIPT_DIR/system_dist/kgcli

#venv\Scripts\activate
pyinstaller --onefile --name kgcli main_cli.py


cp -R $SCRIPT_DIR/dist/kgcli $SCRIPT_DIR/system_dist/kgcli
chmod +x $SCRIPT_DIR/system_dist/kgcli