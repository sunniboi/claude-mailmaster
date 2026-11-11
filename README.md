# MailMaster

Claude-Plugin zum Lesen und Senden von E-Mails aus beliebigen IMAP-Postfächern (Gmail, Freenet, GMX, web.de, Yahoo und andere).

## Installation

In Claude Code eingeben:

    /plugin marketplace add sunniboi/claude-mailmaster
    /plugin install mailmaster@mailmaster-plugins

Danach Claude Code neu starten.

## Einrichtung

Beim ersten Start öffnet sich das Einrichtungsfenster automatisch, wenn noch kein Postfach eingerichtet ist. Später geht es über:

    /mailmaster:setup

Im Fenster E-Mail-Adresse eingeben, der Server wird automatisch gefunden, dann das Passwort einfügen und „Testen und speichern“ klicken. Bei Gmail und Yahoo braucht es ein App-Passwort, die Schritte stehen im Fenster.

## So benutzt du es im Chat

Einfach in Claude schreiben, was du wissen willst, zum Beispiel:

- „Zeig mir meine ungelesenen Mails.“
- „Gibt es neue Mails von Amazon?“
- „Suche Mails mit dem Betreff Rechnung von dieser Woche.“
- „Schreib an test@example.com: Betreff Hallo, Text: Wie geht es dir?“

Beim Senden erscheint vorher ein Fenster mit Absender, Empfänger, Betreff und Text. Erst nach deinem Ja geht die Mail raus.

Das Plugin zeigt Absender, Datum und Betreff. Den vollständigen Mailtext liest es derzeit nicht vor.

## Update

    /plugin marketplace update mailmaster-plugins
    /plugin update mailmaster@mailmaster-plugins

Danach Claude Code neu starten.

## Was es kann

- Postfächer durchsuchen (ungelesene, Absender, Datum, Betreff)
- Mails senden, aber nur nach Bestätigung im Fenster auf dem Bildschirm

## Hinweise

- Getestet nur unter Linux. Windows und macOS sind **nicht getestet**.
- Passwörter liegen im Schlüsselbund des Systems auf dem jeweiligen Rechner. Sie werden nie an einen Server oder in den Chat übertragen.
- Die Einrichtung ist pro Rechner nötig.
- Im Cloud-Chat und auf dem Handy funktioniert das Plugin nicht. Es läuft nur auf dem Rechner, auf dem es installiert ist.

## Sicherheit

- Die Verbindung prüft das Server-Zertifikat.
- Jeder Versand braucht die Bestätigung in einem Fenster auf dem Bildschirm.
