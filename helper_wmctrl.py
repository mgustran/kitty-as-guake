import re
import subprocess


def run_command(argv: list[str]) -> str:
    res = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout


class WmCtrlHelper:

    def get_window_id(self, class_name: str) -> str | None:
        res = run_command(["wmctrl", "-lx"])
        # print(res)

        for line in res.splitlines():
            if class_name in line:
                return line.split()[0]  # primer "campo" (como awk '{print $1}')
        return None

    def set_window_initial_config(self, win_id: str) -> None:
        subprocess.run(["wmctrl", "-ir", win_id, "-b", "add,skip_taskbar"])
        subprocess.run(["wmctrl", "-ir", win_id, "-b", "add,above"])

    def minimize_window(self, win_id: str) -> None:
        subprocess.run(["xdotool", "windowminimize", win_id])

    def maximize_window(self, win_id: str) -> None:
        # subprocess.run(["wmctrl", "-r", win_id, "-b", "remove,maximized_vert,maximized_horz"])
        # subprocess.run(["xdotool", "windowraise", win_id])
        subprocess.run(["xdotool", "windowactivate", "--sync", win_id])

    def resize_window(self, win_id: str, x: int, y: int, width: int, height: int) -> None:
        subprocess.run(["wmctrl", "-ir", win_id, "-e", "0," + str(x) + "," + str(y) + "," + str(width) + "," + str(height)])

    def get_window_state(self, win_id: str) -> bool | None:
        res = run_command(["xprop", "-id", win_id, "_NET_WM_STATE"])
        if res.strip() == '':
            return None
        else:
            return '_NET_WM_STATE_HIDDEN' not in res

    def normalize(self, win_id):
        return int(win_id, 16)

    def is_window_focused(self, win_id: str) -> bool:
        # res = run_command(["xprop", "-root", "_NET_ACTIVE_WINDOW"])
        res = run_command(["xprop", "-root", "_NET_ACTIVE_WINDOW"])
        res_id = re.search(r'0x[0-9a-fA-F]+', res).group(0)
        print(res)
        print(win_id)
        # return win_id in res
        return self.normalize(win_id) == self.normalize(res_id.strip())

    def get_window_geometry(self, win_id: str) -> tuple[int, int, int, int, int] | None:
        res = run_command(["wmctrl", "-lG"])

        rows = []
        for line in res.splitlines():
            if win_id not in line:
                continue
            parts = line.split()
            # wmctrl -lG:
            # 0:WIN_ID 1:DESKTOP 2:X 3:Y 4:W 5:H 6:HOST 7..:TITLE
            win_id = parts[0]
            x, y, w, h = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
            rows.append((win_id, x, y, w, h))

        print(rows)

        if len(rows) > 1:
            print("ERROR: Multiple windows found")

        if len(rows) == 1:
            return rows[0]
        else:
            return None

    # def get_panels_geometry(self) -> list[tuple[int, int, int, int, int]]:
    #     res = run_command(["wmctrl", "-lG"])
    #
    #     rows = []
    #     for line in res.splitlines():
    #         if "xfce4-panel" not in line:
    #             continue
    #         parts = line.split()
    #         win_id = parts[0]
    #         x, y, w, h = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
    #         rows.append((win_id, x, y, w, h))
    #
    #     print(rows)
    #
    #     return rows

    def get_monitors(self) -> list[tuple[int, int, int, int]]:
        """
        return monitor list with geometry: [(x, y, width, height), ...]
        """
        out = subprocess.check_output(["xrandr"]).decode()
        monitors = []

        for line in out.splitlines():
            if " connected" in line and "+" in line:
                match = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if match:
                    w, h, x, y = map(int, match.groups())
                    monitors.append((x, y, w, h))
        monitors.sort(key=lambda m: (m[0]))
        return monitors

    def find_window_monitor(self, win_id, monitors):
        geom = self.get_window_geometry(win_id)
        if not geom:
            return None

        wid, wx, wy, ww, wh = geom

        for i, (mx, my, mw, mh) in enumerate(monitors):
            center_x = wx + ww // 2
            center_y = wy + wh // 2
            if mx <= center_x < mx + mw and my <= center_y < my + mh:
                return i  # monitor idx

        return None

    def find_panel_by_monitor(self, monitor_idx):
        panels = self.get_panels_geometry()
        panels.sort(key=lambda p: (p[1]))
        return panels[monitor_idx]