import subprocess
import time
from typing import Optional, List

from helper_config import KgConfig
from helper_hotkeys import GlobalHotKeys
from helper_wmctrl import WmCtrlHelper

class KittyManager:

    def __init__(self, kg_config: KgConfig):
        self.proc: Optional[subprocess.Popen] = None
        self.wm_id: Optional[str] = None
        self.hotkeys = GlobalHotKeys(long_press_threshold=0.5, repeat_interval=0.02)
        self.wmctrl = WmCtrlHelper()
        self.kg_config = kg_config

        self.start_terminal(minimized=True)

    def start_terminal(self, minimized: bool = False) -> None:
        try:
            initial_monitor = int(self.kg_config.config["general"].get("initial_monitor", 0))
        except (ValueError, KeyError):
            initial_monitor = 0

        monitor_list = self.wmctrl.get_monitors()
        if initial_monitor >= len(monitor_list):
            initial_monitor = 0
            
        position_x = monitor_list[initial_monitor][0] if monitor_list else 0
        
        print(f"Starting kitty in monitor {initial_monitor} at position {position_x}")
        
        cmd = [
            "kitty", 
            "-c", str(self.kg_config.KITTY_GEN_CONF),
            "-o", "allow_remote_control=socket-only",
            "--listen-on", "unix:/tmp/mykitty",
            "--position", f"{position_x}x0",
            "--app-id", "kitty-wrapped",
            "--directory", "~"
        ]
        
        if minimized:
            cmd.extend(["--start-as", "minimized"])
            
        self.run_background(cmd)
        print("Kitty started")

    def run_background(self, argv: List[str]) -> None:
        self.proc = subprocess.Popen(argv)

        timeout = 10  # seconds
        start = time.time()
        self.wm_id = None
        
        while time.time() - start < timeout:
            self.wm_id = self.wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
            if self.wm_id:
                break
            time.sleep(0.2)

        if not self.wm_id:
            print("Warning: cannot find kitty window within timeout")
            return

        print(f"{time.time() - start:.2f} seconds to detect kitty window")
        self.wmctrl.set_window_initial_config(self.wm_id)

    def on_activate_resize_up(self) -> None:
        if self.wm_id and self.wmctrl.is_window_focused(self.wm_id):
            geom = self.wmctrl.get_window_geometry(self.wm_id)
            if geom:
                self.wmctrl.resize_window(self.wm_id, -1, -1, -1, geom[4] - 18)

    def on_activate_resize_down(self) -> None:
        if self.wm_id and self.wmctrl.is_window_focused(self.wm_id):
            geom = self.wmctrl.get_window_geometry(self.wm_id)
            if geom:
                self.wmctrl.resize_window(self.wm_id, -1, -1, -1, geom[4] + 18)

    def on_activate_move_left(self) -> None:
        if self.wm_id and self.wmctrl.is_window_focused(self.wm_id):
            monitor_list = self.wmctrl.get_monitors()
            monitor_idx = self.wmctrl.find_window_monitor(self.wm_id, monitor_list)
            if monitor_idx is not None and monitor_idx > 0:
                monitor_target = monitor_list[monitor_idx - 1]
                self.wmctrl.resize_window(self.wm_id, monitor_target[0], 0, monitor_target[2], -1)

    def on_activate_move_right(self) -> None:
        if self.wm_id and self.wmctrl.is_window_focused(self.wm_id):
            monitor_list = self.wmctrl.get_monitors()
            monitor_idx = self.wmctrl.find_window_monitor(self.wm_id, monitor_list)
            if monitor_idx is not None and monitor_idx < len(monitor_list) - 1:
                monitor_target = monitor_list[monitor_idx + 1]
                self.wmctrl.resize_window(self.wm_id, monitor_target[0], 0, monitor_target[2], -1)

    def on_activate_visibility_toggle(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            self.start_terminal()
            return

        if not self.wm_id:
            self.wm_id = self.wmctrl.get_window_id("kitty-wrapped.kitty-wrapped")
            if not self.wm_id:
                return

        visible = self.wmctrl.get_window_state(self.wm_id)
        if visible:
            if not self.wmctrl.is_window_focused(self.wm_id):
                self.wmctrl.maximize_window(self.wm_id)
            else:
                self.wmctrl.minimize_window(self.wm_id)
        else:
            self.wmctrl.maximize_window(self.wm_id)

    def run(self) -> None:
        hotkeys_cfg = self.kg_config.config.get("hotkeys", {})
        
        def get_hk(name):
            return hotkeys_cfg.get(name, "").replace("\"", "")

        keys = {
            get_hk("hotkey_resize_up"): self.on_activate_resize_up,
            get_hk("hotkey_resize_down"): self.on_activate_resize_down,
            get_hk("hotkey_move_left"): self.on_activate_move_left,
            get_hk("hotkey_move_right"): self.on_activate_move_right,
            get_hk("hotkey_visibility_toggle"): self.on_activate_visibility_toggle
        }

        # Filter out empty hotkeys
        keys = {k: v for k, v in keys.items() if k}
        self.hotkeys.start(keys)