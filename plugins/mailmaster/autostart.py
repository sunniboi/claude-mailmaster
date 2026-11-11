#!/usr/bin/env python3
"""Beim Start von Claude Code: Update nur nach Zustimmung anbieten, und Einrichtung, wenn noch kein Postfach da ist."""

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).parent
sys.path.insert(0, str(HIER))

KONFIG = Path.home() / ".config/mail-reader/accounts.json"
MERKER = Path.home() / ".config/mail-reader/update_abgelehnt.txt"
SETUP = HIER / "setup_gui.py"
REMOTE_VERSION = "https://raw.githubusercontent.com/sunniboi/claude-mailmaster/main/plugins/mailmaster/.claude-plugin/plugin.json"


def version_von(text):
    return tuple(int(x) for x in json.loads(text)["version"].split("."))


def eingerichtet():
    try:
        return bool(json.loads(KONFIG.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return False


def neue_version():
    try:
        with urllib.request.urlopen(REMOTE_VERSION, timeout=5) as antwort:
            remote = antwort.read().decode("utf-8")
        installiert = (HIER / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        if version_von(remote) > version_von(installiert):
            return json.loads(remote)["version"], json.loads(installiert)["version"]
    except (OSError, ValueError, KeyError):
        pass
    return None


def nachfragen(neu, alt):
    if MERKER.exists() and MERKER.read_text(encoding="utf-8").strip() == neu:
        return False
    try:
        import tkinter as tk
        from tkinter import messagebox
        from i18n import t
    except ImportError:
        return False
    try:
        wurzel = tk.Tk()
    except tk.TclError:
        return False
    wurzel.withdraw()
    wurzel.attributes("-topmost", True)
    try:
        ja = messagebox.askyesno(t("upd_title"), t("upd_text", version=neu, now=alt), parent=wurzel)
    finally:
        wurzel.destroy()
    if not ja:
        MERKER.parent.mkdir(parents=True, exist_ok=True)
        MERKER.write_text(neu, encoding="utf-8")
    return ja


def installieren():
    befehl = ("claude plugin marketplace update mailmaster-plugins >/dev/null 2>&1; "
              "claude plugin update mailmaster@mailmaster-plugins >/dev/null 2>&1")
    subprocess.Popen(["sh", "-c", befehl], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def main():
    if sys.platform != "win32":
        ergebnis = neue_version()
        if ergebnis and nachfragen(*ergebnis):
            installieren()
    if not eingerichtet():
        try:
            subprocess.Popen([sys.executable, str(SETUP)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=sys.platform != "win32")
        except OSError:
            pass


if __name__ == "__main__":
    main()
