import subprocess


def run(argv: list[str]) -> int:
    proc = subprocess.run(argv)
    return proc.returncode


if __name__ == "__main__":
    run(["kitty", "-c", "/home/mgustran/00-development/kitty-wrapper/kitty.conf", "--position", "1920x0"])

# wmctrl -lx                                                          (list windows)
# wmctrl -ia 0x08e0000b                                               (focus window by id)

# Sintaxis: wmctrl -ir <WIN_ID> -e <gravity>,<X>,<Y>,<W>,<H>
# wmctrl -ir 0x01234567 -e 0,200,100,-1,-1                            (move window)

# wmctrl -ir :ACTIVE: -e 0,0,0,800,600                                (resize window)

# wmctrl -ir 0x08e0000b -b add,skip_taskbar                           (remove app from taskbar)

# xdotool windowminimize 0x08e0000b                                   (hide window - in fact is minimizing, but as there is no app in taskbar counts as hiding)
# xdotool windowraise 0x08e0000b                                      (unhide window)

# fastfetch --kitty /home/mgustran/Software/System/icons/Debian_logo_white.png         (init splash screen with real png)

