import os
import platform
import sys
import threading
from typing import TYPE_CHECKING, Optional

import gi

from helper_file import FileHelper

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf

if TYPE_CHECKING:
    from helper_kitty import KittyManager

# def get_resource_path(relative_path: str) -> str:
#     # Get absolute path to resource, works for dev and for PyInstaller
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         # Assuming we are in helper_systray.py and images are in project root
#         base_path = os.path.dirname(os.path.abspath(__file__))
#
#     path = os.path.join(base_path, relative_path)
#     # If not found (maybe when running from different directory in dev), try project root
#     if not os.path.exists(path):
#          base_path = os.path.abspath(".")
#          path = os.path.join(base_path, relative_path)
#     return path

class KittySystray:
    def __init__(self, manager: "KittyManager"):
        self.manager = manager
        self.icon: Optional[Gtk.StatusIcon] = None
        self._loop: Optional[GLib.MainLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start_systray_in_thread(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._thread = threading.Thread(
                target=self.run_systray_loop,
                name="gtk-systray",
                daemon=True,
            )
            self._thread.start()

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def stop(self) -> None:
        if self._loop:
            GLib.idle_add(self._loop.quit)

    def run_systray_loop(self) -> None:
        GLib.idle_add(self.create_systray)
        self._loop = GLib.MainLoop()
        self._loop.run()

    def create_systray(self) -> None:
        if platform.system() != "Linux":
            return

        unique_id = f"com.mgustran.kitty.{os.getpid()}"
        GLib.set_prgname(unique_id)
        GLib.set_application_name('Kitty Manager')

        self.icon = Gtk.StatusIcon()
        icon_path = str(FileHelper.get_resource_path("images_gui/kitty.png"))

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.icon.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")
            self.icon.set_from_icon_name("utilities-terminal")

        self.icon.set_tooltip_text("Kitty Manager")
        self.icon.connect("popup-menu", self.on_right_click)
        self.icon.connect("activate", self.on_left_click)
        self.icon.set_visible(True)

    def on_left_click(self, icon: Gtk.StatusIcon) -> None:
        print("Left click: Toggle window")
        self.manager.on_activate_visibility_toggle()

    def on_right_click(self, icon: Gtk.StatusIcon, button: int, activate_time: int) -> None:
        menu = Gtk.Menu()

        item_open = Gtk.MenuItem(label="Open/Focus Kitty")
        item_open.connect("activate", self._on_menu_open)
        menu.append(item_open)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", self._on_menu_quit)
        menu.append(item_quit)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, activate_time)

    def _on_menu_open(self, widget: Gtk.MenuItem) -> None:
        if self.manager.wm_id:
            self.manager.wmctrl.maximize_window(self.manager.wm_id)
        else:
            self.manager.start_terminal()

    def _on_menu_quit(self, widget: Gtk.MenuItem) -> None:
        print("Quitting application...")
        if self.manager.proc and self.manager.proc.poll() is None:
            self.manager.proc.terminate()
        
        self.manager.hotkeys.stop()
        self.stop()
        sys.exit(0)
