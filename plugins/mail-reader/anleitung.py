"""App-Passwort-Anleitung für Gmail und Yahoo, öffnet die Anbieterseite in Chrome."""

import os
import shutil
import subprocess
import sys
import webbrowser

from i18n import t

CHROME_PFADE = {
    "linux": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
    "win32": [
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
    ],
}

URLS = {
    "gmail": "https://myaccount.google.com/apppasswords",
    "yahoo": "https://login.yahoo.com/account/security",
}


def chrome_finden():
    for pfad in CHROME_PFADE.get(sys.platform, CHROME_PFADE["linux"]):
        gefunden = shutil.which(pfad) if os.sep not in pfad else (pfad if os.path.exists(pfad) else None)
        if gefunden:
            return gefunden
    return None


def öffne_in_chrome(url):
    chrome = chrome_finden()
    if chrome:
        subprocess.Popen([chrome, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    webbrowser.open(url)
    return False


def anbieter_schlüssel(host):
    for schlüssel in URLS:
        if schlüssel in host:
            return schlüssel
    return None


def anleitung(schlüssel):
    return {
        "url": URLS[schlüssel],
        "titel": t(f"{schlüssel}_title"),
        "schritte": [t(f"{schlüssel}_{n}") for n in range(1, 6)],
    }
