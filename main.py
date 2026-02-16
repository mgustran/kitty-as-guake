from helper_config import KgConfig
from helper_kitty import KittyManager
from helper_systray import KittySystray
from helper_wmctrl import WmCtrlHelper


class KittyRunner:

    def __init__(self):
        # todo: validate kitty, wmctrl, xdotool is installed

        self.config = KgConfig()
        self.config.init_config()

        self.manager = KittyManager(self.config)
        self.systray = KittySystray(manager=self.manager)

        # todo: redo this, make it non-dependant from systray loop
        self.manager.run()
        self.systray.run_systray_loop()

if __name__ == "__main__":
    print("starting kitty-guake 0")
    # todo: prevent run more than once
    wmctrl_helper = WmCtrlHelper()
    win_idx = wmctrl_helper.get_window_id("kitty-wrapped.kitty-wrapped")

    if win_idx is None:
        print("starting kitty-guake")
        KittyRunner()
    else:
        print("kitty-guake already running: " + str(win_idx))
        exit(0)