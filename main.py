from helper_kitty import KittyManager
from helper_systray import KittySystray


class KittyRunner:

    def __init__(self):

        self.manager = KittyManager()
        self.systray = KittySystray(manager=self.manager)

        # todo: redo this, make it non-dependant from systray loop
        self.manager.run()
        self.systray.run_systray_loop()

if __name__ == "__main__":
    KittyRunner()