import time
import threading
from typing import Dict, Callable, Set, Tuple, Optional, FrozenSet
from pynput import keyboard

class GlobalHotKeys:

    def __init__(self, long_press_threshold: float = 0.5, repeat_interval: float = 0.02):
        """
        :param long_press_threshold: seconds to consider long press
        :param repeat_interval: interval between autorepeat calls
        """
        self.long_press_threshold = long_press_threshold
        self.repeat_interval = repeat_interval

        self._pressed_keys: Set[keyboard.Key | keyboard.KeyCode] = set()
        self._active_combos: Dict[FrozenSet, Callable] = {}
        self._threads: Dict[FrozenSet, Tuple[threading.Thread, threading.Event]] = {}
        self._lock = threading.Lock()

        self.listener: Optional[keyboard.Listener] = None

    def _parse_hotkey(self, hotkey: str) -> FrozenSet:
        parts = hotkey.lower().replace("<", "").replace(">", "").split("+")
        parsed = set()

        for part in parts:
            part = part.strip()
            if not part:
                continue
            if hasattr(keyboard.Key, part):
                parsed.add(getattr(keyboard.Key, part))
            else:
                if len(part) == 1:
                    parsed.add(keyboard.KeyCode.from_char(part))
                else:
                    special = {
                        "alt_l": keyboard.Key.alt_l,
                        "alt_r": keyboard.Key.alt_r,
                        "ctrl_l": keyboard.Key.ctrl_l,
                        "ctrl_r": keyboard.Key.ctrl_r,
                        "shift_l": keyboard.Key.shift_l,
                        "shift_r": keyboard.Key.shift_r,
                    }
                    if part in special:
                        parsed.add(special[part])
                    else:
                        raise ValueError(f"Invalid Hotkey part: {part}")

        return frozenset(parsed)

    def on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            self._pressed_keys.add(key)

            for combo, callback in self._active_combos.items():
                if combo.issubset(self._pressed_keys):
                    # Only init thread if not exist or dead
                    if combo not in self._threads or not self._threads[combo][0].is_alive():
                        self._start_repeat_thread(combo, callback)

    def on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            self._pressed_keys.discard(key)

            to_stop = [combo for combo in self._threads if not combo.issubset(self._pressed_keys)]
            for combo in to_stop:
                self._stop_repeat_thread(combo)

    def _start_repeat_thread(self, combo: FrozenSet, callback: Callable) -> None:
        stop_event = threading.Event()

        def runner():
            start_time = time.time()
            first_call = True
            while not stop_event.is_set():
                try:
                    if first_call:
                        callback()
                        first_call = False
                    else:
                        if (time.time() - start_time) >= self.long_press_threshold:
                            callback()
                except Exception as e:
                    print(f"Error in hotkey callback {combo}: {e}")
                
                time.sleep(self.repeat_interval)

        t = threading.Thread(target=runner, daemon=True)
        self._threads[combo] = (t, stop_event)
        t.start()

    def _stop_repeat_thread(self, combo: FrozenSet) -> None:
        if combo in self._threads:
            _, stop_event = self._threads.pop(combo)
            stop_event.set()

    def start(self, keys: Dict[str, Callable]) -> None:
        """
        Start the global hotkey listener.
        :param keys: Dictionary mapping hotkey strings to callback functions.
        """
        self.stop_all()
        
        with self._lock:
            self._active_combos.clear()
            for hotkey, callback in keys.items():
                try:
                    combo = self._parse_hotkey(hotkey)
                    self._active_combos[combo] = callback
                except ValueError as e:
                    print(f"Skipping invalid hotkey '{hotkey}': {e}")

            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            print(f"Listening for hotkeys: {list(keys.keys())}")

    def stop_all(self) -> None:
        with self._lock:
            for combo in list(self._threads.keys()):
                self._stop_repeat_thread(combo)
            self._pressed_keys.clear()

    def stop(self) -> None:
        self.stop_all()
        if self.listener:
            self.listener.stop()
            self.listener = None
