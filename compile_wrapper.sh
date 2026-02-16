#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/system_dist
rm -rf $SCRIPT_DIR/build
rm -rf $SCRIPT_DIR/dist/kitty-guake
rm -rf $SCRIPT_DIR/system_dist/kitty-guake


pyinstaller --onefile --hidden-import='gi' --add-data "images_gui:images_gui" --add-data "templates:templates" --name kitty-guake main.py

# todo:remove
cp -R $SCRIPT_DIR/dist/kitty-guake $SCRIPT_DIR/system_dist/kitty-guake
chmod +x $SCRIPT_DIR/system_dist/kitty-guake