# mailmaster

Claude-Plugin zum Lesen von E-Mails aus beliebigen IMAP-Postfächern (Gmail, Freenet, GMX, web.de und andere).

## Installation

In Claude Code:

    /plugin marketplace add sunniboi/claude-mailmaster
    /plugin install mailmaster@mailmaster-plugins

## Einrichtung

Einmal im Terminal ausführen:

    python3 ~/Downloads/mailmaster-marketplace/plugins/mailmaster/setup.py

Das Skript fragt nur E-Mail-Adresse und Passwort ab und findet die Server selbst, wie Thunderbird. Die Passwörter landen in `~/.config/mailmaster/passwords.json` mit Dateirechten nur für dich. Gmail braucht ein App-Passwort, das normale Passwort funktioniert bei IMAP nicht.

Danach Claude Code neu starten.

## Werkzeuge

- `list_accounts`: zeigt die eingerichteten Postfächer.
- `search_mail`: sucht im Posteingang mit IMAP-Suche, z. B. `UNSEEN`, `FROM "amazon"`, `SINCE 10-Nov-2026`.

Das Plugin liest nur. Es sendet oder verändert keine Mails.

## Hinweise

- Getestet nur unter Linux. Windows und macOS sind **nicht getestet**.
- Passwörter werden im Schlüsselbund des Systems gespeichert (Windows-Anmeldeinformationsverwaltung, macOS-Schlüsselbund, Linux Secret Service). Dafür installiert das Setup beim ersten Mal nach Zustimmung das Paket `keyring`.

## Sicherheit

- Die Verbindung prüft das Server-Zertifikat.
- Passwörter liegen nur im Schlüsselbund des Systems, nie im Repo und nie auf einem Server.
