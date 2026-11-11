# mail-reader

Claude-Plugin zum Lesen von E-Mails aus beliebigen IMAP-Postfächern (Gmail, Freenet, GMX, web.de und andere).

## Installation

In Claude Code:

    /plugin marketplace add sunniboi/claude-mail-reader
    /plugin install mail-reader@mail-reader-plugins

## Einrichtung

Einmal im Terminal ausführen:

    python3 ~/Downloads/mail-reader-marketplace/plugins/mail-reader/setup.py

Das Skript fragt nur E-Mail-Adresse und Passwort ab und findet die Server selbst, wie Thunderbird. Die Passwörter landen in `~/.config/mail-reader/passwords.json` mit Dateirechten nur für dich. Gmail braucht ein App-Passwort, das normale Passwort funktioniert bei IMAP nicht.

Danach Claude Code neu starten.

## Werkzeuge

- `list_accounts`: zeigt die eingerichteten Postfächer.
- `search_mail`: sucht im Posteingang mit IMAP-Suche, z. B. `UNSEEN`, `FROM "amazon"`, `SINCE 10-Nov-2026`.

Das Plugin liest nur. Es sendet oder verändert keine Mails.

## Sicherheit

- Die Verbindung prüft das Server-Zertifikat.
- Passwörter liegen nur lokal im Konfigurationsordner, nie im Repo.
