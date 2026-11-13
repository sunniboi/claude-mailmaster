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
- Online-Variante: Mit **html** kann eine HTML-Fassung (Fettdruck, Absätze) mitgesendet werden. Die Freigabeseite zeigt sie in einer Vorschau ohne Skripte.
- **Sendelimit (Online-Variante):** Pro Postfach höchstens 10 Mails pro Stunde, insgesamt höchstens 30. Das schützt vor Massenversand. Einstellbar über `MAILMASTER_MAX_PRO_STUNDE` und `MAILMASTER_MAX_GESAMT_PRO_STUNDE`. Empfänger sind nicht eingeschränkt.
- **Entwürfe:** `create_draft` legt einen Entwurf im Entwürfe-Ordner des Kontos ab, ohne zu senden.
- **Antworten:** `reply_mail` antwortet auf eine Mail per UID. Die Antwort hängt sich mit In-Reply-To und References an den Verlauf.

## Ordner

- **Alle Ordner eines Kontos anzeigen:** Spam, Papierkorb, Gesendet, Entwürfe und eigene Ordner. Die Namen kommen direkt vom Anbieter.
- **In einem Ordner suchen oder lesen:** Der Standard ist der Posteingang, ein anderer Ordner kann angegeben werden.
- **In allen Ordnern suchen:** Eine Suche über alle Ordner eines Kontos, mit Ordnername je Treffer. Ordner, die nicht geöffnet werden können, werden übersprungen.
- **Papierkorb festlegen (empfohlen, wenn Löschen nicht klappt):** In der Cloud Shell `cd server && python3 set_trash.py <adresse> <ordnername>`, z. B. `python3 set_trash.py sunniboi@freenet.de INBOX.Trash`. Den Ordnernamen zeigt `list_folders`. Der Dienst wird danach aktualisiert.
- **Löschen:** `delete_mail` verschiebt die Mail in den Papierkorb des Kontos. Den Papierkorb erkennt der Server am Anbieter-Flag `\Trash` (bei Freenet z. B. `INBOX.Trash`). Nichts wird endgültig entfernt.
- **Verschieben:** `move_mail` nennt den Zielordner. Auch „Papierkorb“, „Spam“, „Gesendet“, „Entwürfe“ und „Archiv“ werden dem echten Ordnernamen zugeordnet. Die Mail wird mit MOVE oder UID EXPUNGE aus dem Quellordner entfernt. Wenn der Anbieter beides nicht kann, wird vorher abgebrochen und nichts kopiert, damit keine Doppel entstehen.
- **Ordner anlegen:** `create_folder`.

## Anhänge

- `list_attachments` zeigt die Anhänge einer Mail (Name, Typ, Größe).
- `download_attachment` holt einen Anhang: Textdateien als Text, Bilder und andere Dateien als Datei (höchstens 5 MB). Ob Claude den Inhalt einer PDF lesen kann, hängt vom Programm ab, mit dem du Claude nutzt.

## Lesen

Mailtexte gelten als **unvertrauenswürdige Daten**. Sie werden im Ausgabetext deutlich gekennzeichnet. Eine Mail kann Anweisungen enthalten, die Claude nicht ausführen darf. Claude soll Mailinhalte nur anzeigen und zusammenfassen. Wenn nur eine HTML-Fassung vorhanden ist, wird der Text daraus gewonnen.

## Verbindungen

Pro Postfach läuft immer nur eine Verbindung gleichzeitig. Bei Verbindungsabbrüchen wird es noch zweimal versucht. Ein falsches Passwort wird nicht wiederholt, und die Fehlermeldung zeigt die genaue Antwort des Anbieters.

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
