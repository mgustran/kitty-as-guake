# kitty-as-guake
### (Kitty "Guake-style" drop-down terminal)

![](https://i.postimg.cc/CKY0XGxh/kitty-guake-v1.gif)

A small wrapper around **[Kitty terminal](https://sw.kovidgoyal.net/kitty/)** for **Linux** to make it behave like a **Guake / drop-down terminal**:


- Launches a Kitty window with a stable `app-id` so it can be found reliably.
- Toggle **focus/show/hide** via a **global hotkey**.
- **Move between multiple monitors** and **resize** the window with hotkeys.
- Includes a **GTK3 systray icon** with a simple menu (open / quit).
- Many of the features available on guake can be configured through native kitty config. 

> Warn: This is a very basic and **very** early-stage project, made specifically to work in xfce/x11 and at the moment only will be tested on Debian13+xfce4.
> Can contain bugs and security issues. Probably there are other projects than can perform better or to be better written (maybe harder to configure too).

---

### Requirements

- **Linux distro using x11 graphical environment**
- These tools **must be available** in your PATH and are usually available on most distros:
  - `kitty wmctrl xdotool xprop xrandr`
  - on debian-based distros: `sudo apt install kitty wmctrl xdotool xprop xrandr`

### Setup
- Get binaries
  - Option 1: Download prebuilt binaries from the releases page.
  - Option 2: Build it yourself
- (optional, but recommended): Set binaries inside a PATH folder

### Build
- Clone the repo
- (optional but recommended) Create a python3 virtualenv and activate it
- Run `pip install -r requirements.txt`
- Run `bash compile_wrapper.sh` to build the main binary
- Run `bash compile_cli.sh` to build the cli binary
- The binaries will be in the `dist` folder

### Usage
#### Kitty Wrapper
- Run by the first time and this will generate two config files in `~/.config/kitty-guake`
  - `./kitty-guake`
  - You can now modify `~/.config/kitty-guake/kitty-guake.conf` to set your hotkeys
  - If you need, you can change the default kitty config file in `~/.config/kitty-guake/kitty.conf`
  - **DONT** modify the `generated.conf` file, as will be overrided on every start

#### Remote control
- Run `kgcli ` to control the kitty-guake wrapper remotely. (this is useful to integrate wrapper into the system)
  - example: `./kgcli --show true --cmd "launch --type=tab ~"` will open a new tab in ~ inside the running kitty instance
  - `--show true` will show the window if minimized 
  - `--cmd <command>` will run the command on the kitty instance
  - **NOTE**: the command is a kitten command, not bash or anything else. Kitten reference: https://sw.kovidgoyal.net/kitty/remote-control/#remote-control-via-a-socket

### Why?
- I wanted a simple and stable way to launch a kitty terminal in a drop-down style and maintain some features from guake as more window control.
- I am a guake long-time user and want to have a custom-maintained and minimal terminal.
- Uncomplicated to configure across all my computers
- The main and real reason for all of this is that is wanted to see the album covers from [spotify-player](https://github.com/aome510/spotify-player) and guake does not support that