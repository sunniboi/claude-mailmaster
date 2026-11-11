#!/usr/bin/env python3
"""Einrichtung für mail-reader wie in Thunderbird: Adresse und Passwort eingeben, Server werden automatisch gefunden."""

import getpass
import imaplib
import json
import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from anleitung import anbieter_schlüssel, anleitung, öffne_in_chrome

ORDNER = Path.home() / ".config/mail-reader"
KONFIG = ORDNER / "accounts.json"
PASSWORT_DATEI = ORDNER / "passwords.json"


def lade_xml(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as antwort:
            return ET.fromstring(antwort.read())
    except Exception:
        return None


def server_aus_xml(wurzel):
    imap = wurzel.find(".//incomingServer[@type='imap']")
    smtp = wurzel.find(".//outgoingServer[@type='smtp']")
    if imap is None or not imap.findtext("hostname"):
        return None
    ergebnis = {"host": imap.findtext("hostname"), "port": int(imap.findtext("port") or 993)}
    if smtp is not None and smtp.findtext("hostname"):
        ergebnis["smtp_host"] = smtp.findtext("hostname")
        ergebnis["smtp_port"] = int(smtp.findtext("port") or 587)
        ergebnis["smtp_starttls"] = (smtp.findtext("socketType") or "").upper() != "SSL"
    return ergebnis


def erkenne_server(domain):
    quellen = [
        f"https://autoconfig.thunderbird.net/v1.1/{domain}",
        f"https://autoconfig.{domain}/mail/config-v1.1.xml",
        f"https://{domain}/.well-known/autoconfig/mail/config-v1.1.xml",
    ]
    for url in quellen:
        wurzel = lade_xml(url)
        if wurzel is not None:
            gefunden = server_aus_xml(wurzel)
            if gefunden:
                return gefunden
    return {
        "host": f"imap.{domain}", "port": 993,
        "smtp_host": f"smtp.{domain}", "smtp_port": 587, "smtp_starttls": True,
    }


def lade(datei):
    return json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else {}


def speichere_geschützt(datei, daten):
    ORDNER.mkdir(parents=True, exist_ok=True)
    fd = os.open(datei, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)


def teste_anmeldung(server, adresse, passwort):
    try:
        imap = imaplib.IMAP4_SSL(server["host"], server["port"], ssl_context=ssl.create_default_context())
        imap.login(adresse, passwort)
        imap.logout()
        return None
    except Exception as e:
        return str(e)


def main():
    try:
        einrichten()
    except (KeyboardInterrupt, EOFError):
        print("\nAbgebrochen. Bereits eingerichtete Postfächer sind gespeichert.")


def einrichten():
    konten = json.loads(KONFIG.read_text(encoding="utf-8")) if KONFIG.exists() else []
    passwoerter = lade(PASSWORT_DATEI)
    print("Mail-Reader einrichten. Bei der Adresse leer lassen, um fertig zu werden.")
    while True:
        adresse = input("\nE-Mail-Adresse: ").strip()
        if not adresse:
            break
        if "@" not in adresse:
            print("Das sieht nicht nach einer E-Mail-Adresse aus.")
            continue
        domain = adresse.split("@", 1)[1].lower()
        print(f"Suche Server für {domain} ...")
        server = erkenne_server(domain)
        print(f"Gefunden: {server['host']}:{server['port']}")
        schlüssel = anbieter_schlüssel(server["host"])
        if schlüssel:
            daten = anleitung(schlüssel)
            print(daten["titel"])
            for nummer, schritt in enumerate(daten["schritte"], 1):
                print(f"  {nummer}. {schritt}")
            öffne_in_chrome(daten["url"])
        passwort = getpass.getpass("Passwort (unsichtbar): ")
        fehler = teste_anmeldung(server, adresse, passwort)
        if fehler:
            print(f"Anmeldung fehlgeschlagen: {fehler}")
            print("Prüfe Passwort, App-Passwort und ob IMAP beim Anbieter aktiviert ist.")
            continue
        print("Anmeldung erfolgreich.")
        konten = [k for k in konten if k["user"] != adresse]
        konten.append({"label": adresse, "user": adresse, **{k: v for k, v in server.items()}})
        passwoerter[adresse] = passwort
        speichere_geschützt(KONFIG, konten)
        speichere_geschützt(PASSWORT_DATEI, passwoerter)
        print(f"{adresse} ist verbunden und gespeichert.")
        if input("\nNoch eine E-Mail-Adresse einrichten?\n  1) Beenden\n  2) Weitere einrichten\nWahl: ").strip() != "2":
            break
    print(f"\nFertig: {len(konten)} Postfächer gespeichert in {ORDNER}")


if __name__ == "__main__":
    main()
