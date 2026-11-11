"""Passwörter im Schlüsselbund des Systems. Alte Klartext-Datei wird beim Lesen übernommen und gelöscht."""

import json
import subprocess
import sys
from pathlib import Path

DIENST = "mail-pilot"
ALTE_DATEI = Path.home() / ".config/mail-reader/passwords.json"
LIBS = Path.home() / ".local/share/mail-pilot/libs"

if LIBS.exists() and str(LIBS) not in sys.path:
    sys.path.insert(0, str(LIBS))


def keyring_verfügbar():
    try:
        import keyring  # noqa: F401
        return True
    except ImportError:
        return False


def keyring_installieren():
    LIBS.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--target", str(LIBS), "keyring"],
                       check=True, timeout=300, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.SubprocessError, OSError):
        return False
    if str(LIBS) not in sys.path:
        sys.path.insert(0, str(LIBS))
    return keyring_verfügbar()


def _alte_datei_übernehmen(adresse):
    if not ALTE_DATEI.exists() or not keyring_verfügbar():
        return None
    daten = json.loads(ALTE_DATEI.read_text(encoding="utf-8"))
    if adresse not in daten:
        return None
    import keyring
    keyring.set_password(DIENST, adresse, daten.pop(adresse))
    if daten:
        ALTE_DATEI.write_text(json.dumps(daten, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        ALTE_DATEI.unlink()
    return keyring.get_password(DIENST, adresse)


def passwort_lesen(adresse):
    if keyring_verfügbar():
        import keyring
        gespeichert = keyring.get_password(DIENST, adresse)
        if gespeichert:
            return gespeichert
        return _alte_datei_übernehmen(adresse)
    if ALTE_DATEI.exists():
        return json.loads(ALTE_DATEI.read_text(encoding="utf-8")).get(adresse)
    return None


def passwort_speichern(adresse, passwort):
    import keyring
    keyring.set_password(DIENST, adresse, passwort)
