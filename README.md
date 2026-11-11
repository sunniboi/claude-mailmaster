# mail-reader

Claude-Plugin zum Lesen von E-Mails aus beliebigen IMAP-Postfächern (Gmail, Freenet, GMX, web.de, eigene Domains).

## Installation

    /plugin marketplace add <GITHUB-URL-DIESES-REPOS>
    /plugin install mail-reader@sunniboi-plugins

## Einrichtung

1. Konfigurationsdatei `~/.config/mail-reader/accounts.json` anlegen:

        [
          {"label": "Freenet", "host": "imap.freenet.de", "port": 993,
           "user": "name@freenet.de", "password_env": "MAIL_FREENET_PASSWORD"}
        ]

2. Passwort als Umgebungsvariable setzen (nie in der Datei speichern):

        export MAIL_FREENET_PASSWORD='dein_passwort'

3. Gmail braucht ein App-Passwort (Google-Konto → Sicherheit → App-Passwörter), das normale Passwort funktioniert bei IMAP nicht.

## Werkzeuge

- `list_accounts`: zeigt die konfigurierten Postfächer.
- `search_mail`: sucht im Posteingang mit IMAP-Suche, z. B. `UNSEEN`, `FROM "amazon"`, `SINCE 10-Nov-2026`.

Das Plugin liest nur. Es sendet oder verändert keine Mails.
