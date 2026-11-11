"""Schritt-für-Schritt-Anleitung für App-Passwörter, öffnet die Anbieterseite im Browser."""

import webbrowser

APP_PASSWORT_ANLEITUNG = {
    "gmail": {
        "url": "https://myaccount.google.com/apppasswords",
        "titel": "Google: App-Passwort erstellen",
        "schritte": [
            "Die Seite öffnet sich. Melde dich mit deinem Google-Konto an, falls nötig.",
            "Wenn dort steht „Bestätigung in zwei Schritten ist nicht aktiviert“: zuerst die Bestätigung in zwei Schritten einschalten, dann die Seite erneut öffnen.",
            "Im Feld „App-Name“ z. B. „Mail-Reader“ eingeben und auf „Erstellen“ klicken.",
            "Es erscheint ein 16-stelliges Passwort. Es wird nur einmal angezeigt: kopieren.",
            "Hier im Setup beim Passwort genau dieses Passwort einfügen (Leerzeichen sind egal).",
        ],
    },
    "yahoo": {
        "url": "https://login.yahoo.com/account/security",
        "titel": "Yahoo: App-Passwort erstellen",
        "schritte": [
            "Die Seite öffnet sich. Melde dich mit deinem Yahoo-Konto an, falls nötig.",
            "Suche den Bereich „App-Passwörter“ bzw. „Apps verwalten“ und klicke auf „App-Passwort generieren“.",
            "Als App-Name z. B. „Mail-Reader“ eingeben und bestätigen.",
            "Es erscheint ein Passwort. Es wird nur einmal angezeigt: kopieren.",
            "Hier im Setup beim Passwort genau dieses Passwort einfügen, nicht dein Yahoo-Login-Passwort.",
        ],
    },
}


def anbieter_schlüssel(host):
    for schlüssel in APP_PASSWORT_ANLEITUNG:
        if schlüssel in host:
            return schlüssel
    return None


def zeige_anleitung(host, öffnen=True):
    schlüssel = anbieter_schlüssel(host)
    if schlüssel is None:
        return None
    anleitung = APP_PASSWORT_ANLEITUNG[schlüssel]
    print(f"\n{anleitung['titel']}")
    for nummer, schritt in enumerate(anleitung["schritte"], 1):
        print(f"  {nummer}. {schritt}")
    if öffnen:
        webbrowser.open(anleitung["url"])
        print(f"  (Seite im Browser geöffnet: {anleitung['url']})")
    return anleitung["url"]
