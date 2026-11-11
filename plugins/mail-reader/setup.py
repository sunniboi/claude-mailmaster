#!/usr/bin/env python3
"""Einrichtung für mail-reader: fragt Postfächer und Passwörter ab und speichert sie lokal."""

import getpass
import json
import os
from pathlib import Path

ORDNER = Path.home() / ".config/mail-reader"
KONFIG = ORDNER / "accounts.json"
PASSWORT_DATEI = ORDNER / "passwords.json"

ANBIETER = {
    "1": ("Gmail / Google Workspace", "imap.gmail.com", "App-Passwort nötig: myaccount.google.com → Sicherheit → App-Passwörter"),
    "2": ("Freenet", "imap.freenet.de", "IMAP muss in den Freenet-Einstellungen aktiviert sein"),
    "3": ("GMX", "imap.gmx.net", "IMAP in den GMX-Einstellungen aktivieren"),
    "4": ("web.de", "imap.web.de", "IMAP in den web.de-Einstellungen aktivieren"),
    "5": ("Anderer Anbieter", None, "IMAP-Server des Anbieters eingeben"),
}


def frage_anbieter():
    print("\nAnbieter wählen:")
    for nummer, (name, host, _) in ANBIETER.items():
        print(f"  {nummer}) {name}")
    while True:
        wahl = input("Nummer: ").strip()
        if wahl in ANBIETER:
            return ANBIETER[wahl]
        print("Bitte eine Nummer von 1 bis 5 wählen.")


def lade(datei):
    return json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else []


def speichere_geschützt(datei, daten):
    ORDNER.mkdir(parents=True, exist_ok=True)
    fd = os.open(datei, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)


def main():
    konten = lade(KONFIG)
    passwoerter = json.loads(PASSWORT_DATEI.read_text(encoding="utf-8")) if PASSWORT_DATEI.exists() else {}
    print("Mail-Reader einrichten. Bei der Adresse leer lassen, um fertig zu werden.")
    while True:
        name, host, hinweis = frage_anbieter()
        if host is None:
            host = input("IMAP-Server (z. B. imap.example.com): ").strip()
        adresse = input("E-Mail-Adresse: ").strip()
        if not adresse:
            break
        print(f"Hinweis: {hinweis}")
        passwort = getpass.getpass("Passwort (unsichtbar): ")
        konto = {"label": f"{name} – {adresse}", "host": host, "port": 993, "user": adresse}
        konten = [k for k in konten if k["user"] != adresse] + [konto]
        if passwort:
            passwoerter[adresse] = passwort
        weiter = input("Noch ein Postfach? [j/N] ").strip().lower()
        if weiter != "j":
            break
    speichere_geschützt(KONFIG, konten)
    speichere_geschützt(PASSWORT_DATEI, passwoerter)
    print(f"\nFertig: {len(konten)} Postfächer gespeichert in {ORDNER}")


if __name__ == "__main__":
    main()
