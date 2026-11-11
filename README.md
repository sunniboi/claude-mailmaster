# MailMaster

Claude-Erweiterung zum Lesen und Senden von E-Mails aus eigenen Postfächern (Gmail, Yahoo, Freenet, web.de und andere mit IMAP).

Es gibt zwei Varianten:

| Variante | Wo es läuft | Für wen |
|---|---|---|
| **A: Plugin in Claude Code** | auf deinem Rechner | jeder, der Claude Code nutzt |
| **B: Online-Server (Connector)** | auf einem Server bei Google Cloud | nur für den Betreiber und Nutzer, die das selbst aufsetzen |

## A: Plugin in Claude Code

In Claude Code eingeben:

    /plugin marketplace add sunniboi/claude-mailmaster
    /plugin install mailmaster@mailmaster-plugins

Danach Claude Code neu starten. Beim ersten Start öffnet sich das Einrichtungsfenster, wenn noch kein Postfach eingerichtet ist. Später über `/mailmaster:setup`.

Im Fenster E-Mail-Adresse eingeben. Der Server wird automatisch gefunden. Dann das Passwort eingeben und „Testen und speichern“ klicken.

**Updates:** Beim Start fragt das Plugin, ob eine neue Version installiert werden soll. Dafür erscheint ein Fenster.

## B: Online-Server für Claude im Browser und am Handy

Diese Variante läuft auf einem Server bei Google Cloud. Claude im Browser und in der App spricht mit diesem Server. Sie ist technisch aufwendiger als Variante A.

Einrichtung in Kurzform:

1. Ein Google-Cloud-Konto anlegen (Testzeitraum mit Guthaben, Kreditkarte zur Prüfung).
2. Den Server über die Cloud Shell aus diesem Repo veröffentlichen (Ordner `server/`, Skript `update.py`).
3. Die Postfächer mit App-Passwörtern eintragen (Skripte in der Cloud Shell).
4. In Claude unter Einstellungen → Konnektoren einen benutzerdefinierten Konnektor mit der Server-Adresse anlegen. Authentifizierung: Keine.

Wichtig:
- Die Passwörter liegen bei dieser Variante als Umgebungsvariablen im Google-Cloud-Projekt. Nur der Projekt-Besitzer kann sie sehen. Sie landen nie im Repo.
- Die Server-Adresse enthält ein Geheimnis. Wer sie kennt, kann auf die Postfächer zugreifen. Nicht teilen.

## Senden

- Claude zeigt dir die Mail im Chat (Absender, Empfänger, Betreff, Text).
- Du schreibst **„absenden“**. Erst dann wird gesendet.
- In Variante A kann pro Konto eine Bestätigung im Fenster verlangt werden. Das ist standardmäßig eingeschaltet.

## Lesen

Mailtexte gelten als **unvertrauenswürdige Daten**. Eine Mail kann Anweisungen enthalten, die Claude nicht ausführen darf. Claude soll Mailinhalte nur anzeigen und zusammenfassen.

## Bekannte Einschränkungen

- Getestet nur unter Linux. Windows und macOS sind **nicht getestet**.
- Gmail und Yahoo brauchen ein App-Passwort, das normale Passwort funktioniert nicht.
- web.de braucht ein App-Passwort, und IMAP muss in den web.de-Einstellungen aktiviert sein.
- Freenet nutzt imap.freenet.de bzw. mx.freenet.de.

## Sicherheit

- Variante A: Passwörter liegen im Schlüsselbund des Systems auf deinem Rechner.
- Variante B: Passwörter liegen in Google Cloud Run. Freigaben sind nur für dich möglich.
- Die Verbindung zum Mailserver prüft das Serverzertifikat.
- Mails werden nie an Dritte weitergegeben. Die Server-Adresse aus Variante B gilt als Geheimnis.
