#!/usr/bin/env python3
"""MCP-Server (stdio) zum Lesen von IMAP-Postfächern. Nur Standardbibliothek.

Konfiguration wird mit setup.py erstellt: ~/.config/mail-reader/accounts.json
(Konten) und ~/.config/mail-reader/passwords.json (Passwörter, nur für den Nutzer lesbar).
"""

import email
import imaplib
import json
import os
import ssl
import sys
from email.header import decode_header, make_header
from pathlib import Path

KONFIG = Path(os.environ.get("MAIL_READER_CONFIG", Path.home() / ".config/mail-reader/accounts.json"))


def konten():
    if not KONFIG.exists():
        raise ValueError(f"Konfiguration fehlt: {KONFIG}")
    return json.loads(KONFIG.read_text(encoding="utf-8"))


def konto_wählen(name):
    alle = konten()
    if not name:
        return alle
    treffer = [k for k in alle if k["label"] == name or k["user"] == name]
    if not treffer:
        raise ValueError(f"Konto nicht gefunden: {name}")
    return treffer


PASSWORT_DATEI = Path.home() / ".config/mail-reader/passwords.json"


def verbinde(konto):
    passwoerter = json.loads(PASSWORT_DATEI.read_text(encoding="utf-8")) if PASSWORT_DATEI.exists() else {}
    passwort = passwoerter.get(konto["user"])
    if not passwort:
        raise ValueError(f"Kein Passwort gespeichert für {konto['user']}. Bitte setup.py ausführen.")
    imap = imaplib.IMAP4_SSL(konto["host"], konto.get("port", 993), ssl_context=ssl.create_default_context())
    imap.login(konto["user"], passwort)
    return imap


def lesbar(wert):
    try:
        return str(make_header(decode_header(wert or "")))
    except Exception:
        return wert or ""


def list_accounts(_args):
    return "\n".join(f"{k['label']}: {k['user']} ({k['host']})" for k in konten())


def search_mail(args):
    suche = args.get("search") or "ALL"
    if any(ord(z) < 32 or ord(z) == 127 for z in suche):
        raise ValueError("Suchkriterium enthält unerlaubte Steuerzeichen")
    maximum = min(max(int(args.get("max_results", 5)), 1), 50)
    ausgabe = []
    for konto in konto_wählen(args.get("account")):
        imap = verbinde(konto)
        try:
            imap.select("INBOX", readonly=True)
            _, daten = imap.search(None, suche)
            ids = daten[0].split()[-maximum:]
            ausgabe.append(f"=== {konto['label']} ({konto['user']}) ===")
            for mail_id in reversed(ids):
                _, teile = imap.fetch(mail_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                kopf = email.message_from_bytes(teile[0][1])
                ausgabe.append(
                    f"- {lesbar(kopf['Date'])}\n  Von: {lesbar(kopf['From'])}\n  Betreff: {lesbar(kopf['Subject'])}"
                )
        finally:
            imap.logout()
    return "\n".join(ausgabe)


WERKZEUGE = {
    "list_accounts": {
        "beschreibung": "Listet die konfigurierten Postfächer auf.",
        "schema": {"type": "object", "properties": {}},
        "funktion": list_accounts,
    },
    "search_mail": {
        "beschreibung": (
            "Sucht im Posteingang. 'search' ist eine IMAP-Suche, z. B. 'ALL', 'UNSEEN', "
            "'FROM \"amazon\"', 'SINCE 10-Nov-2026', 'SUBJECT \"Code\"'. "
            "Ohne 'account' werden alle Konten durchsucht."
        ),
        "schema": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "IMAP-Suchkriterium, Standard ALL"},
                "account": {"type": "string", "description": "Label oder Adresse eines Kontos, optional"},
                "max_results": {"type": "integer", "description": "Mails pro Konto, Standard 5"},
            },
        },
        "funktion": search_mail,
    },
}


def antworte(id_, ergebnis=None, fehler=None):
    nachricht = {"jsonrpc": "2.0", "id": id_}
    if fehler:
        nachricht["error"] = {"code": -32000, "message": fehler}
    else:
        nachricht["result"] = ergebnis
    sys.stdout.write(json.dumps(nachricht) + "\n")
    sys.stdout.flush()


def main():
    for zeile in sys.stdin:
        zeile = zeile.strip()
        if not zeile:
            continue
        anfrage = json.loads(zeile)
        methode = anfrage.get("method")
        id_ = anfrage.get("id")
        if id_ is None:
            continue
        try:
            if methode == "initialize":
                antworte(id_, {
                    "protocolVersion": anfrage["params"].get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mail-reader", "version": "0.2.0"},
                })
            elif methode == "tools/list":
                antworte(id_, {"tools": [
                    {"name": n, "description": w["beschreibung"], "inputSchema": w["schema"]}
                    for n, w in WERKZEUGE.items()
                ]})
            elif methode == "tools/call":
                name = anfrage["params"]["name"]
                args = anfrage["params"].get("arguments", {}) or {}
                text = WERKZEUGE[name]["funktion"](args)
                antworte(id_, {"content": [{"type": "text", "text": text}]})
            else:
                antworte(id_, fehler=f"Unbekannte Methode: {methode}")
        except Exception as e:
            antworte(id_, {"content": [{"type": "text", "text": f"Fehler: {e}"}], "isError": True})


if __name__ == "__main__":
    main()
