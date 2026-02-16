import os
import platform
import sys
import threading
from typing import TYPE_CHECKING

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf

if TYPE_CHECKING:
    from helper_kitty import KittyManager

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class KittySystray:
    def __init__(self, manager: "KittyManager"):
        self.manager = manager
        self.icon = None
        self._loop: GLib.MainLoop | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def start_systray_in_thread(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return  # prevent run more than once

            self._thread = threading.Thread(
                target=self.run_systray_loop,
                name="gtk-systray",
                daemon=True,
            )
            self._thread.start()

    def is_running(self) -> bool:
        t = self._thread
        return bool(t and t.is_alive())

    def stop(self) -> None:
        loop = self._loop
        if loop is not None:
            GLib.idle_add(loop.quit)

    def run_systray_loop(self) -> None:
        self.create_systray()
        self._loop = GLib.MainLoop()
        self._loop.run()

    def create_systray(self):
        if platform.system() == "Linux":
            unique_id = f"com.mgustran.kitty.{os.getpid()}"
            GLib.set_prgname(unique_id)
            GLib.set_application_name('Kitty Manager')

            self.icon = Gtk.StatusIcon()
            icon_path = resource_path("images_gui/kitty.png")

            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                self.icon.set_from_pixbuf(pixbuf)
            except Exception as e:
                print(f"Error cargando icono: {e}")
                self.icon.set_from_icon_name("applications-system")

            self.icon.set_tooltip_text("Kitty Manager")
            self.icon.connect("popup-menu", self.on_right_click)
            self.icon.connect("activate", self.on_left_click)
            self.icon.set_visible(True)

            return

    def on_left_click(self, icon):
        self.toggle_window()
        print("Left click")

    def on_right_click(self, icon, button, time):
        # Handle right click - show context menu
        print("Right click")
        menu = Gtk.Menu()

        item_open = Gtk.MenuItem(label="Open Kitty")
        item_open.connect("activate", self.show_window)
        menu.append(item_open)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", self.quit_window)
        menu.append(item_quit)

        menu.show_all()
        menu.popup(None, None, None, None, button, time)

    def toggle_window(self, *args):
        print("Toggle window visibility")
        self.manager.on_activate_visibility_toggle()
        pass

    def show_window(self, *args):
        print("Show window")
        self.manager.wmctrl.maximize_window(self.manager.wm_id)
        pass

    def quit_window(self, *args):
        print("Quit window")

        try:
            if self.manager.proc is not None and self.manager.proc.poll() is None:
                self.manager.proc.terminate()
        except Exception as e:
            print("Error cerrando kitty:", e)

        self.manager.hotkeys.stop()

        self.stop()
