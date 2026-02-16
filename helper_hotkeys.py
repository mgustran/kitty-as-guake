import time
import threading
from pynput import keyboard

class GlobalHotKeys:

    def __init__(self, long_press_threshold=1.0, repeat_interval=0.2):
        """
        :param long_press_threshold: seconds to consider long press
        :param repeat_interval: interval between autorepeat calls
        """
        self.long_press_threshold = long_press_threshold
        self.repeat_interval = repeat_interval

        self._pressed_keys = set()
        self._press_times = {}
        self._active_combos = {}
        self._threads = {}

        self.listener = None

    # ------------------------------
    # COMBINATION PARSER
    # ------------------------------
    def _parse_hotkey(self, hotkey):
        parts = hotkey.lower().replace("<", "").replace(">", "").split("+")
        parsed = set()

        for part in parts:
            if hasattr(keyboard.Key, part):
                parsed.add(getattr(keyboard.Key, part))
            else:
                if len(part) == 1:
                    parsed.add(keyboard.KeyCode.from_char(part))
                else:
                    raise ValueError(f"Invalid Hotkey: {part}")

        return frozenset(parsed)

    # ------------------------------
    # LISTENER CALLBACKS
    # ------------------------------
    def on_press(self, key):
        self._pressed_keys.add(key)
        if key not in self._press_times:
            self._press_times[key] = time.time()

        for combo, callback in self._active_combos.items():
            if combo.issubset(self._pressed_keys):
                # Only init thread if not exist or dead
                if combo not in self._threads or not self._threads[combo][0].is_alive():
                    self._start_repeat_thread(combo, callback)

    def on_release(self, key):
        self._pressed_keys.discard(key)
        self._press_times.pop(key, None)

        to_stop = [combo for combo in self._threads if not combo.issubset(self._pressed_keys)]
        for combo in to_stop:
            self._stop_repeat_thread(combo)

        # if key == keyboard.Key.esc:
        #     return False

    # ------------------------------
    # AUTOREPEAT THREAD
    # ------------------------------
    def _start_repeat_thread(self, combo, callback):
        stop_event = threading.Event()

        def runner():
            start_time = time.time()
            first_call = True
            while not stop_event.is_set():
                try:
                    now = time.time()
                    duration = now - start_time
                    if first_call:
                        callback()
                        first_call = False
                    else:
                        if duration >= self.long_press_threshold:
                            callback()
                except Exception as e:
                    print(f"Error en callback del combo {combo}: {e}")
                time.sleep(self.repeat_interval)

        t = threading.Thread(target=runner, daemon=True)
        self._threads[combo] = (t, stop_event)
        t.start()

    def _stop_repeat_thread(self, combo):
        if combo not in self._threads:
            return
        thread, stop_event = self._threads.pop(combo)
        stop_event.set()
        thread.join(timeout=0.1)  # handle block if freeze

    # ------------------------------
    # PUBLIC API
    # ------------------------------
    def start(self, keys):
        self._active_combos.clear()
        for hotkey, callback in keys.items():
            combo = self._parse_hotkey(hotkey)
            self._active_combos[combo] = callback

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        print("Escuchando hotkeys:", keys.keys())

    def stop_all(self):
        for combo in list(self._threads.keys()):
            self._stop_repeat_thread(combo)

    def stop(self):
        self.stop_all()
        if self.listener:
            self.listener.stop()
