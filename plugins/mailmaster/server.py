#!/usr/bin/env python3
"""MCP-Server (stdio) zum Lesen von IMAP-Postfächern. Nur Standardbibliothek.

Konfiguration wird mit setup.py erstellt: ~/.config/mail-reader/accounts.json
(Konten) und ~/.config/mail-reader/passwords.json (Passwörter, nur für den Nutzer lesbar).
"""

import email
import imaplib
import json
import os
import smtplib
import ssl
import sys
from email.header import decode_header, make_header
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup import erkenne_server  # noqa: E402
from bestaetigung import nutzer_bestätigt  # noqa: E402
from geheimnisse import passwort_lesen  # noqa: E402

KONFIG = Path(os.environ.get("MAIL_READER_CONFIG", Path.home() / ".config/mail-reader/accounts.json"))


def konten():
    if not KONFIG.exists():
        raise ValueError("Noch kein Postfach eingerichtet. Bitte /mailmaster:setup ausführen.")
    return json.loads(KONFIG.read_text(encoding="utf-8"))


def konto_wählen(name):
    alle = konten()
    if not name:
        return alle
    treffer = [k for k in alle if k["label"] == name or k["user"] == name]
    if not treffer:
        raise ValueError(f"Konto nicht gefunden: {name}. Bitte /mailmaster:setup ausführen.")
    return treffer




def verbinde(konto):
    passwort = passwort_lesen(konto["user"])
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
        ausgabe.append(f"=== {konto['label']} ({konto['user']}) ===")
        try:
            imap = verbinde(konto)
        except Exception as fehler:
            ausgabe.append(f"  Fehler: {fehler}")
            continue
        try:
            imap.select("INBOX", readonly=True)
            _, daten = imap.search(None, suche)
            ids = daten[0].split()[-maximum:]
            if not ids:
                ausgabe.append("  Keine Mails gefunden.")
            for mail_id in reversed(ids):
                _, teile = imap.fetch(mail_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                kopf = email.message_from_bytes(teile[0][1])
                ausgabe.append(
                    f"- {lesbar(kopf['Date'])}\n  Von: {lesbar(kopf['From'])}\n  Betreff: {lesbar(kopf['Subject'])}"
                )
        except Exception as fehler:
            ausgabe.append(f"  Fehler beim Lesen: {fehler}")
        finally:
            imap.logout()
    return "\n".join(ausgabe)


def postausgang(konto):
    if not konto.get("smtp_host"):
        gefunden = erkenne_server(konto["user"].split("@", 1)[1].lower())
        konto = {**konto, **gefunden}
    return konto


def send_mail(args):
    konten_gefunden = konto_wählen(args.get("account"))
    if len(konten_gefunden) != 1:
        raise ValueError("Bitte genau ein Absenderkonto angeben (Adresse oder Label).")
    konto = konten_gefunden[0]
    empfaenger = args.get("to", "").strip()
    betreff = args.get("subject", "").strip()
    text = args.get("body", "")
    if not empfaenger or "@" not in empfaenger or not betreff:
        raise ValueError("Empfänger (to) und Betreff (subject) sind Pflicht.")
    vorschau = (
        f"VORSCHAU (noch nicht gesendet)\n"
        f"Von: {konto['user']}\nAn: {empfaenger}\nBetreff: {betreff}\n\n{text}"
    )
    if not konto.get("auto_send") and not nutzer_bestätigt(konto["user"], empfaenger, betreff, text):
        return "Abgebrochen. Der Nutzer hat das Senden nicht bestätigt, es wurde nichts gesendet."

    server = postausgang(konto)
    nachricht = EmailMessage()
    nachricht["From"] = konto["user"]
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht.set_content(text)

    passwort = passwort_lesen(konto["user"])
    if not passwort:
        raise ValueError(f"Kein Passwort gespeichert für {konto['user']}. Bitte /mailmaster:setup ausführen.")

    kontext = ssl.create_default_context()
    if server.get("smtp_starttls", True):
        with smtplib.SMTP(server["smtp_host"], server.get("smtp_port", 587), timeout=30) as smtp:
            smtp.starttls(context=kontext)
            smtp.login(konto["user"], passwort)
            smtp.send_message(nachricht)
    else:
        with smtplib.SMTP_SSL(server["smtp_host"], server.get("smtp_port", 465), context=kontext, timeout=30) as smtp:
            smtp.login(konto["user"], passwort)
            smtp.send_message(nachricht)
    return f"Gesendet von {konto['user']} an {empfaenger}."


WERKZEUGE = {
    "send_mail": {
        "beschreibung": (
            "Sendet eine E-Mail von einem eingerichteten Konto. Auf dem Bildschirm des Nutzers "
            "erscheint vorher ein Bestätigungsfenster mit Absender, Empfänger, Betreff und Text. "
            "Die Mail wird nur gesendet, wenn der Nutzer dort selbst zustimmt. Vorher dem Nutzer den Inhalt nennen."
        ),
        "schema": {
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Absenderkonto: Adresse oder Label"},
                "to": {"type": "string", "description": "Empfänger-Adresse"},
                "subject": {"type": "string", "description": "Betreff"},
                "body": {"type": "string", "description": "Text der Mail"},
            },
            "required": ["account", "to", "subject", "body"],
        },
        "funktion": send_mail,
    },
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
                    "serverInfo": {"name": "mailmaster", "version": "0.4.0"},
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
