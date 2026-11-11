import json, os, subprocess, tempfile

svc, reg = "mailmaster", "us-central1"
out = subprocess.run(["gcloud", "run", "services", "describe", svc, "--region", reg, "--format", "json"],
                     capture_output=True, text=True, check=True).stdout
env = json.loads(out)["spec"]["template"]["spec"]["containers"][0].get("env", [])
vals = {e["name"]: e.get("value", "") for e in env}

fd, pfad = tempfile.mkstemp(suffix=".yaml")
try:
    with os.fdopen(fd, "w") as f:
        for k, v in vals.items():
            f.write(f"{k}: '{v}'\n" if k == "MAILMASTER_ACCOUNTS" else f'{k}: "{v}"\n')
    subprocess.run(["gcloud", "run", "deploy", svc, "--source", ".", "--region", reg, "--allow-unauthenticated",
                    "--max-instances", "1", "--memory", "256Mi", "--env-vars-file", pfad], check=True)
finally:
    os.remove(pfad)
print("Aktualisiert.")
