# Übergabe: MailMaster

Eindeutiger Name: **mailmaster@mailmaster-plugins**

- Repo: https://github.com/sunniboi/claude-mailmaster
- Installation in Claude Code: `/plugin marketplace add sunniboi/claude-mailmaster` und `/plugin install mailmaster@mailmaster-plugins`
- Einrichtung: `/mailmaster:setup` oder Fenster beim ersten Start
- Anleitung und Details: siehe README.md

Die Passwörter bleiben beim jeweiligen Nutzer. Die Online-Variante braucht einen eigenen Google-Cloud-Server und ist für Nutzer ohne technische Erfahrung nicht gedacht.

## Online-Server: Werkzeuge (Stand 13.11.2026)

- Lesen und suchen: `list_accounts`, `search_mail`, `read_mail`, `search_all_folders`, `list_folders`
- Anhänge: `list_attachments`, `download_attachment` (Text, Bild oder Datei bis 5 MB)
- Ordner: `create_folder`, `move_mail` (Ziel auch „Papierkorb“, „Spam“, „Gesendet“, „Entwürfe“, „Archiv“), `delete_mail` (in den Papierkorb, nichts wird endgültig gelöscht)
- Senden: `send_mail` (optional `html`), `reply_mail` (Antwort im Verlauf). Beides nur nach Freigabe durch den Nutzer.
- Verschieben nutzt MOVE oder UID EXPUNGE. Ohne beides wird vorher abgebrochen, damit keine Doppel entstehen.
- Papierkorb und Sonderordner werden über die Anbieter-Flags (`\Trash`, `\Junk` usw.) erkannt, sonst über typische Namen.
- Pro Postfach läuft nur eine IMAP-Verbindung gleichzeitig.

**Veröffentlichen:** Nach dem Push auf GitHub muss der Cloud-Run-Dienst aktualisiert werden. In der Cloud Shell: `git pull` im Repo, dann `cd server && python3 update.py`. Erst danach läuft die neue Version.
