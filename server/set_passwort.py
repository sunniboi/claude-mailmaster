"""Trägt das Passwort eines Postfachs neu ein und aktualisiert den Dienst.

Aufruf in der Cloud Shell:
    python3 set_passwort.py <adresse>
Beispiel:
    python3 set_passwort.py r-s-r@freenet.de

Das Passwort wird verdeckt abgefragt (es erscheint nicht auf dem Bildschirm
und landet nicht im Verlauf). Es wird nur in die Cloud-Run-Einstellungen
geschrieben. Andere Postfächer und Einstellungen bleiben unverändert.
"""

import getpass
import json
import os
import subprocess
import sys
import tempfile

svc, reg = "mailmaster", "us-central1"

if len(sys.argv) != 2:
    print("Aufruf: python3 set_passwort.py <adresse>")
    sys.exit(1)
adresse = sys.argv[1].strip()

out = subprocess.run(["gcloud", "run", "services", "describe", svc, "--region", reg, "--format", "json"],
                     capture_output=True, text=True, check=True).stdout
env = json.loads(out)["spec"]["template"]["spec"]["containers"][0].get("env", [])
vals = {e["name"]: e.get("value", "") for e in env}

konten = json.loads(vals.get("MAILMASTER_ACCOUNTS", "[]"))
treffer = [k for k in konten if k.get("user") == adresse or k.get("label") == adresse]
if not treffer:
    print(f"Kein Konto mit '{adresse}' gefunden. Vorhanden: {', '.join(k.get('user', '?') for k in konten)}")
    sys.exit(1)

passwort = getpass.getpass(f"Neues Passwort für {adresse} (wird nicht angezeigt): ")
if not passwort:
    print("Kein Passwort eingegeben. Nichts geändert.")
    sys.exit(1)
for k in treffer:
    k["password"] = passwort
del passwort
vals["MAILMASTER_ACCOUNTS"] = json.dumps(konten)

# JSON ist gültiges YAML, so bleiben Anführungszeichen im Passwort erhalten.
fd, pfad = tempfile.mkstemp(suffix=".yaml")
try:
    with os.fdopen(fd, "w") as f:
        for k, v in vals.items():
            f.write(f"{k}: {json.dumps(v)}\n")
    subprocess.run(["gcloud", "run", "deploy", svc, "--source", ".", "--region", reg, "--allow-unauthenticated",
                    "--max-instances", "1", "--memory", "256Mi", "--env-vars-file", pfad], check=True)
finally:
    os.remove(pfad)
print(f"Passwort für {adresse} wurde gespeichert. Der Dienst wurde aktualisiert.")
