# Übergabe: mail-reader (Claude-Plugin für E-Mails)

## Eindeutiger Name

Den Namen **immer vollständig** angeben, weil es viele Mail-Reader gibt:

    mail-reader@mail-reader-plugins

- Repo: https://github.com/sunniboi/claude-mail-reader
- Marketplace: `mail-reader-plugins`
- Plugin: `mail-reader`

## Installation (auf jedem Rechner einmal)

In Claude Code eingeben:

    /plugin marketplace add sunniboi/claude-mail-reader
    /plugin install mail-reader@mail-reader-plugins

Danach Claude Code neu starten.

## Einrichten

    /mail-reader:setup

Es öffnet sich ein Fenster. E-Mail-Adresse eingeben, Passwort einfügen, „Testen und speichern“. Bei Gmail und Yahoo braucht es ein App-Passwort, die Schritte stehen im Fenster.

## Was es kann

- Postfächer durchsuchen (ungelesene, Absender, Datum, Betreff)
- Mails senden, aber nur nach Bestätigung in einem Fenster auf dem Bildschirm

## Wichtige Grenzen

- Läuft nur auf dem Rechner, auf dem es installiert ist.
- Im Cloud-Chat und auf dem Handy funktioniert es **nicht**, dafür wäre ein Server nötig.
- Passwörter bleiben lokal auf dem Rechner, sie gehen nie in den Chat.
