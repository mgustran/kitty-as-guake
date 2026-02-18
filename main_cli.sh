#!/usr/bin/env bash

get_version() {
    echo "0.1.1"
}

get_window_id() {
    local class_name="$1"
    wmctrl -lx | grep "$class_name" | awk '{print $1}' | head -n 1
}

maximize_window() {
    local win_id="$1"
    xdotool windowactivate --sync "$win_id"
}

CMD=""
SHOW=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --cmd)
            CMD="$2"
            shift 2
            ;;
        --show)
            SHOW=true
            shift
            ;;
        --version)
            echo "kgcli version (bash): $(get_version)"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

WIN_ID=$(get_window_id "kitty-wrapped.kitty-wrapped")

if [[ "$SHOW" == true ]]; then
    if [[ -n "$WIN_ID" ]]; then
        maximize_window "$WIN_ID"
    else
        echo "Warning: Window not found, cannot show."
    fi
fi

if [[ -n "$CMD" ]]; then
    if command -v kitten >/dev/null 2>&1; then
#      echo $CMD
        kitten @ --to unix:/tmp/mykitty $CMD
    else
        echo "Error: 'kitten' command not found."
    fi
elif [[ "$SHOW" == false ]]; then
    echo "No command or show flag provided."
fi
