# Übergabe: mail-pilot (Claude-Plugin für E-Mails)

## Eindeutiger Name

Den Namen **immer vollständig** angeben, weil es viele Mail-Programme gibt:

    mail-pilot@mail-pilot-plugins

- Repo: https://github.com/sunniboi/claude-mail-pilot
- Marketplace: `mail-pilot-plugins`
- Plugin: `mail-pilot`

## Installation (auf jedem Rechner einmal)

In Claude Code eingeben:

    /plugin marketplace add sunniboi/claude-mail-pilot
    /plugin install mail-pilot@mail-pilot-plugins

Danach Claude Code neu starten.

## Einrichten

    /mail-pilot:setup

Es öffnet sich ein Fenster. E-Mail-Adresse eingeben, Passwort einfügen, „Testen und speichern“. Bei Gmail und Yahoo braucht es ein App-Passwort, die Schritte stehen im Fenster.

## Was es kann

- Postfächer durchsuchen (ungelesene, Absender, Datum, Betreff)
- Mails senden, aber nur nach Bestätigung in einem Fenster auf dem Bildschirm

## Wichtige Grenzen

- Läuft nur auf dem Rechner, auf dem es installiert ist.
- Im Cloud-Chat und auf dem Handy funktioniert es **nicht**, dafür wäre ein Server nötig.
- Passwörter liegen im Schlüsselbund des Systems auf dem Rechner, sie gehen nie in den Chat und nie an einen Server.
- Getestet nur unter Linux. Windows und macOS sind nicht getestet.
