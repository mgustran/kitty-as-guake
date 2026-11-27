---
apply: always
---

# CONTEXTO PROYECTO: kitty-as-guake

## Qué es
- Wrapper Python para Kitty terminal en Linux.
- Hace que Kitty actúe como terminal desplegable estilo Guake.
- Pensado para X11 + XFCE. Solo probado en Debian 13 + XFCE4.
- Proyecto temprano: puede tener bugs y problemas de seguridad.

## Funciones
- Lanza Kitty con `app-id` estable para encontrar la ventana.
- Hotkey global: dar foco / mostrar / ocultar.
- Hotkeys para mover entre monitores y cambiar tamaño.
- Icono de bandeja del sistema con GTK3 (abrir / salir).
- Control remoto con `kgcli` mediante comandos kitten.

## Dependencias del sistema
- Deben estar en PATH: `kitty`, `wmctrl`, `xdotool`, `xprop`, `xrandr`.
- Solo X11. Wayland no soportado.

## Estructura
- `main.py`: wrapper principal.
- `main_cli.py`: CLI Python.
- `kgcli.sh`: CLI en bash. Más rápida, probable opción por defecto.
- `helper_config.py`: configuración.
- `helper_file.py`: archivos.
- `helper_hotkeys.py`: hotkeys globales.
- `helper_kitty.py`: interacción con Kitty y control remoto.
- `helper_systray.py`: bandeja GTK3.
- `helper_wmctrl.py`: control de ventanas X11 (wmctrl/xdotool).
- `templates/`: plantillas de configuración. `templates/tab_bar.py` es código de terceros (@cdelledonne).
- `compile_wrapper.sh` / `compile_cli.sh`: build con PyInstaller hacia `dist/`.

## Configuración (usuario)
- Ruta: `~/.config/kitty-guake/`.
- `kitty-guake.conf`: hotkeys y opciones del wrapper.
- `kitty.conf`: configuración de Kitty del usuario.
- `generated.conf`: se regenera en cada arranque. NO editar a mano ni proponer cambios ahí.

## Build
- `pip install -r requirements.txt` (mejor dentro de un virtualenv).
- `bash compile_wrapper.sh` y `bash compile_cli.sh`.

## kgcli
- `--show`: muestra la ventana si está minimizada.
- `--cmd "<cmd>"`: ejecuta un comando kitten de control remoto, no bash.
- Ejemplo: `kgcli --show --cmd "launch --type=tab ~"`.

## Reglas para la IA
- Suponer Linux + X11. No proponer soluciones solo para Wayland, macOS o Windows.
- Para ventanas, preferir las herramientas existentes: wmctrl, xdotool, xprop, xrandr.
- Mantener la separación de lógica en los `helper_*.py`.
- Mantener compatibles las versiones bash y Python de kgcli.
- Mantener compatibilidad con el build de PyInstaller (rutas, recursos, imports).
- Para controlar Kitty, usar su control remoto (kitten / socket).
- Cambios simples y mínimos. Proyecto pequeño.
- Licencia MIT. Respetar la atribución de terceros.