import re
import subprocess
from typing import List, Tuple, Optional


def run_command(argv: List[str]) -> str:
    try:
        res = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(argv)}: {e}")
        return ""
    except FileNotFoundError:
        print(f"Command not found: {argv[0]}")
        return ""


class WmCtrlHelper:

    def get_window_id(self, class_name: str) -> Optional[str]:
        res = run_command(["wmctrl", "-lx"])
        for line in res.splitlines():
            if class_name in line:
                return line.split()[0]
        return None

    def set_window_initial_config(self, win_id: str) -> None:
        run_command(["wmctrl", "-ir", win_id, "-b", "add,skip_taskbar"])
        run_command(["wmctrl", "-ir", win_id, "-b", "add,above"])

        monitor_list = self.get_monitors()
        monitor_idx = self.find_window_monitor(win_id, monitor_list)
        if monitor_idx is not None:
            self.resize_window(win_id, -1, -1, monitor_list[monitor_idx][2], -1)

    def minimize_window(self, win_id: str) -> None:
        run_command(["xdotool", "windowminimize", win_id])

    def maximize_window(self, win_id: str) -> None:
        run_command(["xdotool", "windowactivate", "--sync", win_id])

    def resize_window(self, win_id: str, x: int, y: int, width: int, height: int) -> None:
        # -e <G>,<X>,<Y>,<W>,<H>
        gravity = 0
        run_command(["wmctrl", "-ir", win_id, "-e", f"{gravity},{x},{y},{width},{height}"])

    def get_window_state(self, win_id: str) -> Optional[bool]:
        res = run_command(["xprop", "-id", win_id, "_NET_WM_STATE"])
        if not res or "not found" in res.lower():
            return None
        return '_NET_WM_STATE_HIDDEN' not in res

    def _normalize_id(self, win_id: str) -> int:
        try:
            return int(win_id, 16)
        except ValueError:
            return 0

    def is_window_focused(self, win_id: str) -> bool:
        res = run_command(["xprop", "-root", "_NET_ACTIVE_WINDOW"])
        match = re.search(r'0x[0-9a-fA-F]+', res)
        if not match:
            return False
        res_id = match.group(0)
        return self._normalize_id(win_id) == self._normalize_id(res_id)

    def get_window_geometry(self, win_id: str) -> Optional[Tuple[str, int, int, int, int]]:
        res = run_command(["wmctrl", "-lG"])
        target_id_norm = self._normalize_id(win_id)

        for line in res.splitlines():
            parts = line.split()
            if len(parts) < 6:
                continue
            
            curr_id = parts[0]
            if self._normalize_id(curr_id) == target_id_norm:
                # 0:WIN_ID 1:DESKTOP 2:X 3:Y 4:W 5:H
                return (curr_id, int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]))

        return None

    def get_monitors(self) -> List[Tuple[int, int, int, int]]:
        # Return monitor list with geometry: [(x, y, width, height), ...]
        try:
            out = run_command(["xrandr"])
        except Exception:
            return []

        monitors = []
        for line in out.splitlines():
            if " connected" in line and "+" in line:
                match = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if match:
                    w, h, x, y = map(int, match.groups())
                    monitors.append((x, y, w, h))
        monitors.sort(key=lambda m: m[0])
        return monitors

    def find_window_monitor(self, win_id: str, monitors: List[Tuple[int, int, int, int]]) -> Optional[int]:
        geom = self.get_window_geometry(win_id)
        if not geom:
            return None

        _, wx, wy, ww, wh = geom
        center_x = wx + ww // 2
        center_y = wy + wh // 2

        for i, (mx, my, mw, mh) in enumerate(monitors):
            if mx <= center_x < mx + mw and my <= center_y < my + mh:
                return i
        return None