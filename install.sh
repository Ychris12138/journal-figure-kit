#!/usr/bin/env bash
# Journal Figure Kit bootstrap; Bash 3.2+ (macOS, Linux, WSL, Git Bash).
# Optional overrides: JFK_PYTHON (executable), JFK_INSTALLER (local install.py).

jfk_main() {
    set -euo pipefail
    local version='0.11.0'
    local probe='import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'
    local candidate location
    local -a python_cmd=()

    if [[ -n "${JFK_PYTHON:-}" ]]; then
        if "$JFK_PYTHON" -c "$probe" >/dev/null 2>&1; then
            python_cmd=("$JFK_PYTHON")
        fi
    else
        for candidate in python3 python; do
            location="$(command -v "$candidate" 2>/dev/null || true)"
            case "$location" in *WindowsApps*|'') continue ;; esac
            if "$candidate" -c "$probe" >/dev/null 2>&1; then
                python_cmd=("$candidate")
                break
            fi
        done
        if [[ ${#python_cmd[@]} -eq 0 ]] && command -v py >/dev/null 2>&1; then
            if py -3.12 -c "$probe" >/dev/null 2>&1; then
                python_cmd=(py -3.12)
            elif py -3 -c "$probe" >/dev/null 2>&1; then
                python_cmd=(py -3)
            fi
        fi
    fi
    if [[ ${#python_cmd[@]} -eq 0 ]]; then
        echo 'Journal Figure Kit needs Python 3.12 or newer. Install Python, or set JFK_PYTHON to its executable path.' >&2
        return 1
    fi

    printf 'Journal Figure Kit v%s - using %s\n' "$version" "${python_cmd[*]}"
    if [[ -n "${JFK_INSTALLER:-}" ]]; then
        if [[ ! -f "$JFK_INSTALLER" ]]; then
            echo 'JFK_INSTALLER must point to an existing local install.py.' >&2
            return 1
        fi
        exec "${python_cmd[@]}" "$JFK_INSTALLER" --quick "$@"
    fi
    local url="https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/v${version}/install.py"
    exec "${python_cmd[@]}" -c "from urllib.request import urlopen; exec(urlopen('$url', timeout=60).read())" --quick "$@"
}

jfk_main "$@"
