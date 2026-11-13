"""Trägt den Papierkorb-Ordner eines Postfachs ein und aktualisiert den Dienst.

Aufruf in der Cloud Shell:
    python3 set_trash.py <adresse> <ordnername>
Beispiel:
    python3 set_trash.py sunniboi@freenet.de INBOX.Trash

Der Ordnername muss genau so heißen, wie ihn der Anbieter nutzt (mit list_folders in Claude anzeigen lassen).
"""

import json
import os
import subprocess
import sys
import tempfile

svc, reg = "mailmaster", "us-central1"

if len(sys.argv) != 3:
    print("Aufruf: python3 set_trash.py <adresse> <ordnername>")
    sys.exit(1)
adresse, ordner = sys.argv[1].strip(), sys.argv[2].strip()

out = subprocess.run(["gcloud", "run", "services", "describe", svc, "--region", reg, "--format", "json"],
                     capture_output=True, text=True, check=True).stdout
env = json.loads(out)["spec"]["template"]["spec"]["containers"][0].get("env", [])
vals = {e["name"]: e.get("value", "") for e in env}

konten = json.loads(vals.get("MAILMASTER_ACCOUNTS", "[]"))
treffer = [k for k in konten if k.get("user") == adresse or k.get("label") == adresse]
if not treffer:
    print(f"Kein Konto mit '{adresse}' gefunden. Vorhanden: {', '.join(k.get('user', '?') for k in konten)}")
    sys.exit(1)
for k in treffer:
    k["trash_folder"] = ordner
vals["MAILMASTER_ACCOUNTS"] = json.dumps(konten)

# JSON ist gültiges YAML, so bleiben Anführungszeichen in Passwörtern korrekt erhalten.
fd, pfad = tempfile.mkstemp(suffix=".yaml")
try:
    with os.fdopen(fd, "w") as f:
        for k, v in vals.items():
            f.write(f"{k}: {json.dumps(v)}\n")
    subprocess.run(["gcloud", "run", "deploy", svc, "--source", ".", "--region", reg, "--allow-unauthenticated",
                    "--max-instances", "1", "--memory", "256Mi", "--env-vars-file", pfad], check=True)
finally:
    os.remove(pfad)
print(f"Papierkorb für {adresse} ist jetzt '{ordner}'. Der Dienst wurde aktualisiert.")
