---
name: read-mail
description: Use when the user asks to check, search, or find emails in their own mailboxes, e.g. for verification codes, new messages, or mail from a specific sender. Reads mail through the mail-reader MCP tools over IMAP.
---

# Mails lesen (IMAP)

Dieser Skill nutzt die MCP-Werkzeuge des Plugins `mail-reader`.

## Vorgehen

1. Bei Unsicherheit über die Postfächer zuerst `list_accounts` aufrufen.
2. Mit `search_mail` suchen. Das Suchfeld ist eine IMAP-Suche:
   - `ALL` für alle Mails
   - `UNSEEN` für ungelesene
   - `FROM "absender"` oder `SUBJECT "Code"`
   - `SINCE 10-Nov-2026` für Mails ab einem Datum
   - Kombinationen wie `UNSEEN FROM "amazon"` sind erlaubt
3. Wenn der Nutzer nur ein Postfach meint, `account` mit Label oder Adresse setzen.
4. Ergebnis kurz zusammenfassen. Bei Codes den Code und den Absender nennen.

## Einrichtung

Wenn noch kein Postfach eingerichtet ist, sag dem Nutzer, dass er `/mail-reader:setup` ausführen soll.

## Grenzen

- Es werden nur Mails aus dem Posteingang gelesen, nichts wird gesendet oder verändert.
- Die Suche liefert Absender, Datum und Betreff, nicht den vollen Mailtext.
- Zugangsdaten stehen nie im Chat. Sie kommen aus Umgebungsvariablen.
