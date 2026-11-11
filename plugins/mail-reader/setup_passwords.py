#!/usr/bin/env python3
"""Fragt die Passwörter der konfigurierten Postfächer verdeckt ab und speichert sie lokal (nur für dich lesbar)."""

import getpass
import json
import os
from pathlib import Path

KONFIG = Path.home() / ".config/mail-reader/accounts.json"
PASSWORT_DATEI = Path.home() / ".config/mail-reader/passwords.json"


def main():
    konten = json.loads(KONFIG.read_text(encoding="utf-8"))
    vorhandene = json.loads(PASSWORT_DATEI.read_text(encoding="utf-8")) if PASSWORT_DATEI.exists() else {}
    for konto in konten:
        name = konto["password_env"]
        if name in vorhandene:
            ueberschreiben = input(f"{konto['user']}: Passwort ist schon gespeichert. Neu eingeben? [j/N] ")
            if ueberschreiben.lower() != "j":
                continue
        vorhandene[name] = getpass.getpass(f"Passwort für {konto['user']} (Eingabe bleibt unsichtbar, Enter zum Überspringen): ")
        if not vorhandene[name]:
            del vorhandene[name]
    PASSWORT_DATEI.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(PASSWORT_DATEI, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as datei:
        json.dump(vorhandene, datei, indent=2)
    print(f"Gespeichert: {PASSWORT_DATEI} ({len(vorhandene)} Passwörter)")


if __name__ == "__main__":
    main()
