import configparser
import os
import shutil
import sys
from pathlib import Path

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)

def convert_mapping(pyinput_mapping: str) -> str:
    return pyinput_mapping.replace("<", "").replace(">", "").replace("\"", "")

class KgConfig:

    def __init__(self):
        self.config = {}

    def init_config(self):
        config_dir = os.path.expanduser("~/.config/kitty-guake")
        os.makedirs(config_dir, exist_ok=True)

        if not Path(config_dir + "/kitty-guake.conf").exists():
            self.copy_to_folder("kitty-guake.conf", config_dir)

        if not Path(config_dir + "/kitty.conf").exists():
            self.copy_to_folder("kitty.conf", config_dir)


        self.config = self.read_conf_to_dict(config_dir + "/kitty-guake.conf")
        self.generate_kitty_conf()

    def generate_kitty_conf(self):
        filepath = Path(self.get_config_path() + "/kitty.conf")
        content = filepath.read_text()

        if self.config['hotkeys']["hotkey_automap"]:
            content += "\n\n\n#------------ GENERATED -------------"
            content += "\nmap " + convert_mapping(self.config["hotkeys"]["hotkey_resize_up"]) + " discard_event"
            content += "\nmap " + convert_mapping(self.config["hotkeys"]["hotkey_resize_down"]) + " discard_event"
            content += "\nmap " + convert_mapping(self.config["hotkeys"]["hotkey_move_left"]) + " discard_event"
            content += "\nmap " + convert_mapping(self.config["hotkeys"]["hotkey_move_right"]) + " discard_event"
            content += "\nmap " + convert_mapping(self.config["hotkeys"]["hotkey_visibility_toggle"]) + " discard_event"
            content += "\n#------------ GENERATED -------------\n"

        filepath_target = Path(self.get_config_path() + "/generated.conf")
        filepath_target.write_text(content)

    def get_config_path(self):
        return os.path.expanduser("~/.config/kitty-guake")

    def read_conf_to_dict(self, filepath, sections=True):
        config = configparser.ConfigParser()
        # config.read(filepath)
        #
        result = {}

        if sections:
            # config = configparser.ConfigParser()
            config.read(filepath)

            result = {}
            for section in config.sections():
                result[section] = {}
                for key, value in config.items(section):
                    result[section][key] = value
        else:
            filepath = Path(filepath)
            content = filepath.read_text()

            content = "[DEFAULT]\n" + content
            config.read_string(content)
            for key, value in config["DEFAULT"].items():
                result[key] = value

        return result


    def copy_to_folder(self, origin_file, target_folder):
        src = resource_path("templates/" + origin_file)
        dst = Path(target_folder + "/" + origin_file)

        if not dst.exists():
            shutil.copy2(src, dst)
            print("file copied to: ", dst)
        else:
            print("already exist:", dst)