import argparse
import subprocess
import sys

from helper_file import FileHelper
from helper_wmctrl import WmCtrlHelper


class MainCli:
    def __init__(self, cmd: str = "", show: bool = False):
        self.cmd = cmd
        self.show = show
        self.wmctrl = WmCtrlHelper()

    def run(self) -> None:
        win_id = self.wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
        
        if self.show:
            if win_id:
                self.wmctrl.maximize_window(win_id)
            else:
                print("Warning: Window not found, cannot show.")

        if self.cmd:
            # todo: Use list for subprocess.run for better safety
            # full_cmd = ["kitten", "@", "--to", "unix:/tmp/mykitty"] + self.cmd.split()
            try:
                # subprocess.run(full_cmd, check=True)
                subprocess.run(["kitten @ --to unix:/tmp/mykitty " + self.cmd], shell=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running command: {e}")
            except FileNotFoundError:
                print("Error: 'kitten' command not found.")
        elif not self.show:
            print("No command or show flag provided.")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Kitty-as-Guake CLI")
    p.add_argument(
        "--cmd",
        default="",
        help="Command to send to kitty (via 'kitten @')",
    )
    p.add_argument(
        "--show",
        action="store_true",
        help="Focus the kitty-guake window",
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="Show the kitty-guake version",
    )
    return p.parse_args()

def main():
    args = parse_args()

    if args.version:
        # print(f"kitty-guake version: {FileHelper.get_version_from_pyproject()}")
        print(f"kgcli version (python): {FileHelper.get_version_from_pyproject()}")
        sys.exit(0)

    cli = MainCli(args.cmd, args.show)
    cli.run()

if __name__ == "__main__":
    main()