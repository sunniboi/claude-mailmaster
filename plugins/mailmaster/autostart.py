#!/usr/bin/env python3
"""Beim Start von Claude Code: Einrichtungsfenster öffnen, wenn noch kein Postfach eingerichtet ist."""

import json
import subprocess
import sys
from pathlib import Path

KONFIG = Path.home() / ".config/mail-reader/accounts.json"
SETUP = Path(__file__).parent / "setup_gui.py"


def eingerichtet():
    try:
        return bool(json.loads(KONFIG.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return False


def main():
    if eingerichtet():
        return
    try:
        subprocess.Popen([sys.executable, str(SETUP)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=sys.platform != "win32")
    except OSError:
        pass


if __name__ == "__main__":
    main()
