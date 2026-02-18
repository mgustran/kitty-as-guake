import argparse
import sys
import os
import fcntl
from helper_config import KgConfig
from helper_file import FileHelper
from helper_kitty import KittyManager
from helper_systray import KittySystray
from helper_wmctrl import WmCtrlHelper

class KittyRunner:
    def __init__(self):
        self.config = KgConfig()
        self.config.init_config()

        self.manager = KittyManager(self.config)
        self.systray = KittySystray(manager=self.manager)

        self.manager.run()
        self.systray.run_systray_loop()

def is_already_running():
    # Check if another instance is already running using a file lock.
    lock_file = os.path.expanduser("~/.config/kitty-guake/kitty-guake.lock")
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    global _lock_file_handle
    _lock_file_handle = open(lock_file, 'w')
    try:
        fcntl.lockf(_lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except IOError:
        return True

def main(cmd_args: argparse.Namespace):

    print(cmd_args)

    if cmd_args.version:
        print(f"kitty-guake version: {FileHelper.get_version_from_pyproject()}")
        sys.exit(0)

    tool_paths = FileHelper.validate_cli_tools(["wmctrl", "kitty", "xdotool", "xprop", "xrandr"])
    # print(f"Validated tools: {tool_paths}")
    if False in tool_paths.values():
        not_found = [tool for tool, path in tool_paths.items() if path is False]
        print(f"Error: The following tools are not installed or not in PATH: {', '.join(not_found)}")
        sys.exit(1)

    print("Starting kitty-guake...")

    wmctrl = WmCtrlHelper()
    if wmctrl.get_monitors() == []:
        print("Error: Could not detect monitors. Is X11 running and wmctrl installed?")

    if is_already_running():
        win_id = wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
        if win_id:
            print(f"kitty-guake already running (win: {win_id}). Focusing...")
            wmctrl.maximize_window(win_id)
        else:
            print("kitty-guake instance lock exists but window not found.")
        sys.exit(0)

    try:
        KittyRunner()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Kitty-as-Guake")
    p.add_argument(
        "--version",
        action="store_true",
        help="Show the kitty-guake version",
    )
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)