import os
import subprocess
import sys
import time

from helper_config import KgConfig
from helper_hotkeys import GlobalHotKeys
from helper_wmctrl import WmCtrlHelper

def get_base_path():
    if getattr(sys, 'frozen', False):
        # from pyinstaller binary
        return os.path.dirname(sys.executable)
    else:
        # from normal script execution
        return os.path.dirname(os.path.abspath(__file__))

class KittyManager:

    def __init__(self, kg_config: KgConfig):
        self.proc = None
        self.wm_id = None
        self.hotkeys = GlobalHotKeys(long_press_threshold=0.5, repeat_interval=0.02)
        self.wmctrl = WmCtrlHelper()
        self.kg_config = kg_config

        self.start_terminal(minimized=True)

    def start_terminal(self, minimized=False):
        # base_path = get_base_path()
        # print("base path : " + base_path)
        # if not Path(base_path + "/kitty.conf").exists():
        #     print("kitty.conf not found")
        #     return
        initial_monitor = int(self.kg_config.config["general"]["initial_monitor"])
        monitor_list = self.wmctrl.get_monitors()
        position_x = monitor_list[initial_monitor][0]
        print(f"Starting kitty in monitor {initial_monitor} at position {position_x}")
        print(monitor_list[initial_monitor])
        cmd = ["kitty", "-c", self.kg_config.get_config_path() + "/generated.conf",
                             "-o", "allow_remote_control=socket-only",
                             "--listen-on", "unix:/tmp/mykitty",
                             # "--start-as", "minimized",
                             # "--single-instance",
                             "--position", str(position_x) + "x0",
                             "--app-id", "kitty-wrapped",
                             "--directory", "~"
                             ]
        if minimized:
            cmd.append("--start-as")
            cmd.append("minimized")
        self.run_background(cmd)
        print("Kitty started")

    def run_background(self, argv: list[str]):
        self.proc = subprocess.Popen(argv)

        timeout = 10  # seconds
        start = time.time()
        self.wm_id = None
        while time.time() - start < timeout:
            self.wm_id = self.wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
            if self.wm_id:
                break
            time.sleep(0.1)

        print(time.time() - start, "seconds to detect kitty window")

        if not self.wm_id:
            raise RuntimeError("cannot find kitty window")

        self.wmctrl.set_window_initial_config(self.wm_id)

    def on_activate_resize_up(self) -> None:
        # print("Captured: Resize Up")

        if self.wmctrl.is_window_focused(self.wm_id):
            window = self.wmctrl.get_window_geometry(self.wm_id)
            self.wmctrl.resize_window(self.wm_id, -1, -1, -1, window[4] - 18)

    def on_activate_resize_down(self) -> None:
        # print("Captured: Resize Down")

        if self.wmctrl.is_window_focused(self.wm_id):
            window = self.wmctrl.get_window_geometry(self.wm_id)
            self.wmctrl.resize_window(self.wm_id, -1, -1, -1, window[4] + 18)

    def on_activate_move_left(self) -> None:
        # print("Captured: Move Left")

        if self.wmctrl.is_window_focused(self.wm_id):
            monitor_list = self.wmctrl.get_monitors()
            monitor_idx = self.wmctrl.find_window_monitor(self.wm_id, monitor_list)
            print(monitor_idx)
            if monitor_idx > 0:
                monitor_target = monitor_list[monitor_idx - 1]
                self.wmctrl.resize_window(self.wm_id, monitor_target[0], 0, monitor_target[2], -1)

    def on_activate_move_right(self) -> None:
        # print("Captured: Move Right")

        if self.wmctrl.is_window_focused(self.wm_id):
            monitor_list = self.wmctrl.get_monitors()
            monitor_idx = self.wmctrl.find_window_monitor(self.wm_id, monitor_list)
            print(monitor_idx)
            if monitor_idx <= len(monitor_list) - 2:
                monitor_target = monitor_list[monitor_idx + 1]
                self.wmctrl.resize_window(self.wm_id, monitor_target[0], 0, monitor_target[2], -1)


    def on_activate_visibility_toggle(self) -> None:
        # print("Captured: Visibility Toggle")

        if self.proc is None or self.proc.poll() is not None:
            self.start_terminal()

        else:
            visible = self.wmctrl.get_window_state(self.wm_id)
            if visible is None:
                print("ERROR: PROCESS RUNNING BUT CANNOT GET STATE")
            if visible:
                if not self.wmctrl.is_window_focused(self.wm_id):
                    # print("Focusing window")
                    self.wmctrl.maximize_window(self.wm_id)
                else:
                    # print("Minimizing window")
                    self.wmctrl.minimize_window(self.wm_id)
            else:
                # print("Maximizing window")
                self.wmctrl.maximize_window(self.wm_id)


    def run(self) -> None:
        # HOTKEY_RESIZE_UP =    "<ctrl>+<shift>+<up>"
        # HOTKEY_RESIZE_DOWN =  "<ctrl>+<shift>+<down>"
        # HOTKEY_RESIZE_LEFT =  "<ctrl>+<shift>+<left>"
        # HOTKEY_RESIZE_RIGHT = "<ctrl>+<shift>+<right>"
        # HOTKEY_VISIBILITY_TOGGLE = "<ctrl>+ñ"

        hotkey_resize_up = self.kg_config.config["hotkeys"]["hotkey_resize_up"].replace("\"", "")
        hotkey_resize_down = self.kg_config.config["hotkeys"]["hotkey_resize_down"].replace("\"", "")
        hotkey_move_left = self.kg_config.config["hotkeys"]["hotkey_move_left"].replace("\"", "")
        hotkey_move_right = self.kg_config.config["hotkeys"]["hotkey_move_right"].replace("\"", "")
        hotkey_visibility_toggle = self.kg_config.config["hotkeys"]["hotkey_visibility_toggle"].replace("\"", "")

        keys = {
            hotkey_resize_up: self.on_activate_resize_up,
            hotkey_resize_down: self.on_activate_resize_down,
            hotkey_move_left: self.on_activate_move_left,
            hotkey_move_right: self.on_activate_move_right,
            hotkey_visibility_toggle: self.on_activate_visibility_toggle
        }

        # self.start_terminal()
        # self.hotkeys.run(keys)
        # print(keys)
        self.hotkeys.start(keys)

# 0x0960000b
# 0x960000b