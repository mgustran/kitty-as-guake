import argparse
import subprocess

from helper_wmctrl import WmCtrlHelper


class MainCli:
    def __init__(self, cmd: str = "", show: bool = "false"):
        self.cmd = cmd
        self.show = show
        self.wmctrl = WmCtrlHelper()

    def run(self):
        win_id = self.wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
        if win_id is None:
            print("Window not found")
            return
        # print(f"Window ID: {win_id}")

        if self.show == "true":
            self.wmctrl.maximize_window(win_id)

        subprocess.run(["kitten @ --to unix:/tmp/mykitty " + self.cmd], shell=True)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Kitty wrapper")
    p.add_argument(
        "--cmd",
        default="",
        help="kitten command (just after @)",
    )
    p.add_argument(
        "--show",
        default="",
        help="show window before command",
    )
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print(args)
    cli = MainCli(args.cmd, args.show)
    cli.run()