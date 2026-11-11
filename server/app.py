"""MailMaster als Online-Server für Claude im Browser und am Handy (MCP über HTTP).

Konfiguration über Umgebungsvariablen:
- MAILMASTER_TOKEN: geheimer Pfad-Teil, den du in Claude als Connector-Adresse einträgst
- MAILMASTER_ACCOUNTS: JSON-Liste der Postfächer inklusive Passwort
"""

import email
import hmac
import imaplib
import json
import os
import smtplib
import ssl
from email.header import decode_header, make_header
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("MAILMASTER_TOKEN", "")
KONTEN = json.loads(os.environ.get("MAILMASTER_ACCOUNTS", "[]"))
PROTOKOLL = "2025-06-18"


def konto_wählen(name):
    if not name:
        return KONTEN
    treffer = [k for k in KONTEN if k.get("label") == name or k["user"] == name]
    if not treffer:
        raise ValueError(f"Konto nicht gefunden: {name}")
    return treffer


def verbinde(konto):
    imap = imaplib.IMAP4_SSL(konto["host"], konto.get("port", 993), ssl_context=ssl.create_default_context())
    imap.login(konto["user"], konto["password"])
    return imap


def lesbar(wert):
    try:
        return str(make_header(decode_header(wert or "")))
    except Exception:
        return wert or ""


def list_accounts(_args):
    return "\n".join(f"{k.get('label', k['user'])}: {k['user']}" for k in KONTEN) or "Keine Postfächer eingerichtet."


def search_mail(args):
    suche = args.get("search") or "ALL"
    if any(ord(z) < 32 or ord(z) == 127 for z in suche):
        raise ValueError("Suchkriterium enthält unerlaubte Steuerzeichen")
    maximum = min(max(int(args.get("max_results", 5)), 1), 50)
    ausgabe = []
    for konto in konto_wählen(args.get("account")):
        ausgabe.append(f"=== {konto['user']} ===")
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
                ausgabe.append(f"- {lesbar(kopf['Date'])}\n  Von: {lesbar(kopf['From'])}\n  Betreff: {lesbar(kopf['Subject'])}")
        except Exception as fehler:
            ausgabe.append(f"  Fehler beim Lesen: {fehler}")
        finally:
            imap.logout()
    return "\n".join(ausgabe)


def send_mail(args):
    konten = konto_wählen(args.get("account"))
    if len(konten) != 1:
        raise ValueError("Bitte genau ein Absenderkonto angeben.")
    konto = konten[0]
    empfaenger = args.get("to", "").strip()
    betreff = args.get("subject", "").strip()
    text = args.get("body", "")
    if not empfaenger or "@" not in empfaenger or not betreff:
        raise ValueError("Empfänger (to) und Betreff (subject) sind Pflicht.")
    if args.get("freigabe") != "absenden":
        return (f"VORSCHAU (noch nicht gesendet)\nVon: {konto['user']}\nAn: {empfaenger}\n"
                f"Betreff: {betreff}\n\n{text}\n\nErst nach dem Wort 'absenden' des Nutzers mit freigabe='absenden' senden.")
    nachricht = EmailMessage()
    nachricht["From"] = konto["user"]
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht.set_content(text)
    kontext = ssl.create_default_context()
    if konto.get("smtp_starttls", True):
        with smtplib.SMTP(konto["smtp_host"], konto.get("smtp_port", 587), timeout=30) as smtp:
            smtp.starttls(context=kontext)
            smtp.login(konto["user"], konto["password"])
            smtp.send_message(nachricht)
    else:
        with smtplib.SMTP_SSL(konto["smtp_host"], konto.get("smtp_port", 465), context=kontext, timeout=30) as smtp:
            smtp.login(konto["user"], konto["password"])
            smtp.send_message(nachricht)
    return f"Gesendet von {konto['user']} an {empfaenger}."


WERKZEUGE = {
    "list_accounts": {
        "beschreibung": "Listet die eingerichteten Postfächer auf.",
        "schema": {"type": "object", "properties": {}},
        "funktion": list_accounts,
    },
    "search_mail": {
        "beschreibung": "Sucht im Posteingang. 'search' ist eine IMAP-Suche, z. B. 'ALL', 'UNSEEN', 'FROM \"amazon\"', 'SINCE 10-Nov-2026'.",
        "schema": {"type": "object", "properties": {
            "search": {"type": "string"}, "account": {"type": "string"}, "max_results": {"type": "integer"}}},
        "funktion": search_mail,
    },
    "send_mail": {
        "beschreibung": ("Sendet eine Mail. Zuerst den Inhalt im Chat zeigen. Erst wenn der Nutzer 'absenden' schreibt, "
                         "mit freigabe='absenden' aufrufen. Ohne diese Freigabe wird nur eine Vorschau erstellt."),
        "schema": {"type": "object", "properties": {
            "account": {"type": "string"}, "to": {"type": "string"}, "subject": {"type": "string"},
            "body": {"type": "string"}, "freigabe": {"type": "string"}},
            "required": ["account", "to", "subject", "body"]},
        "funktion": send_mail,
    },
}


def antwort(id_, ergebnis=None, fehler=None):
    nachricht = {"jsonrpc": "2.0", "id": id_}
    if fehler:
        nachricht["error"] = {"code": -32000, "message": fehler}
    else:
        nachricht["result"] = ergebnis
    return nachricht


def verarbeite(anfrage):
    methode = anfrage.get("method")
    id_ = anfrage.get("id")
    if id_ is None:
        return None
    if methode == "initialize":
        return antwort(id_, {"protocolVersion": anfrage.get("params", {}).get("protocolVersion", PROTOKOLL),
                             "capabilities": {"tools": {}},
                             "serverInfo": {"name": "mailmaster", "version": "1.0.0"}})
    if methode == "tools/list":
        return antwort(id_, {"tools": [{"name": n, "description": w["beschreibung"], "inputSchema": w["schema"]}
                                       for n, w in WERKZEUGE.items()]})
    if methode == "tools/call":
        name = anfrage["params"]["name"]
        args = anfrage["params"].get("arguments", {}) or {}
        try:
            text = WERKZEUGE[name]["funktion"](args)
            return antwort(id_, {"content": [{"type": "text", "text": text}]})
        except Exception as fehler:
            return antwort(id_, {"content": [{"type": "text", "text": f"Fehler: {fehler}"}], "isError": True})
    return antwort(id_, fehler=f"Unbekannte Methode: {methode}")


class Handler(BaseHTTPRequestHandler):
    def _pfad_gültig(self):
        erwartet = f"/mcp/{TOKEN}"
        return bool(TOKEN) and hmac.compare_digest(self.path.split("?")[0].encode(), erwartet.encode())

    def do_POST(self):
        if not self._pfad_gültig():
            self.send_response(404)
            self.end_headers()
            return
        länge = int(self.headers.get("Content-Length", 0))
        try:
            anfrage = json.loads(self.rfile.read(länge) or b"{}")
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        antworten = verarbeite(anfrage)
        if antworten is None:
            self.send_response(202)
            self.end_headers()
            return
        daten = json.dumps(antworten).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(daten)))
        self.end_headers()
        self.wfile.write(daten)

    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
