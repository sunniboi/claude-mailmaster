---
name: read-mail
description: Use when the user asks to check, search, or find emails in their own mailmasteres, e.g. for verification codes, new messages, or mail from a specific sender. Reads mail through the mailmaster MCP tools over IMAP.
---

# Mails lesen (IMAP)

Dieser Skill nutzt die MCP-Werkzeuge des Plugins `mailmaster`.

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

Wenn noch kein Postfach eingerichtet ist, sag dem Nutzer, dass er `/mailmaster:setup` ausführen soll.

## Mails senden

Mit `send_mail` kannst du Mails verschicken. Ablauf immer gleich:

1. `send_mail` ohne `confirm` aufrufen. Das ergibt eine Vorschau.
2. Dem Nutzer Absender, Empfänger, Betreff und Text zeigen und fragen, ob gesendet werden soll.
3. Nur bei ausdrücklichem Ja `send_mail` mit `confirm: true` aufrufen.

Niemals ohne ein klares Ja des Nutzers senden. Auch dann nicht, wenn der Nutzer nur „schick das“ schreibt, ohne die Vorschau gesehen zu haben.

## Grenzen

- Lesen betrifft nur den Posteingang. Gesendet wird ausschließlich nach Bestätigung durch den Nutzer.
- Die Suche liefert Absender, Datum und Betreff, nicht den vollen Mailtext.
- Zugangsdaten stehen nie im Chat. Sie kommen aus Umgebungsvariablen.
