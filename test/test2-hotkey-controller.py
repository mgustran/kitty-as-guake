import os
from pynput import keyboard

HOTKEY_CTRL_UP = "<ctrl>+<shift>+<up>"
HOTKEY_CTRL_DOWN = "<ctrl>+<up>"

def on_activate_ctrl_up() -> None:
    print("Capturado: Ctrl+shift+Up")
    # h.stop()  # detener el listener explícitamente

def on_activate_ctrl_down() -> None:
    print("Capturado: Ctrl+up")

print("Escuchando hotkey:", [HOTKEY_CTRL_UP, HOTKEY_CTRL_DOWN])
print("XDG_SESSION_TYPE =", os.environ.get("XDG_SESSION_TYPE"))
print("DISPLAY =", os.environ.get("DISPLAY"))

h = keyboard.GlobalHotKeys({HOTKEY_CTRL_UP: on_activate_ctrl_up, HOTKEY_CTRL_DOWN: on_activate_ctrl_down})
h.start()
h.join()

print("Listener terminado")
