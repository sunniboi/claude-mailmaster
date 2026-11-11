#!/usr/bin/env python3
"""Einrichtungsfenster für mail-reader: E-Mail-Adresse eingeben, Passwort eingeben, fertig."""

import imaplib
import json
import ssl
import tkinter as tk
from tkinter import messagebox

from anleitung import APP_PASSWORT_ANLEITUNG, anbieter_schlüssel, öffne_in_chrome
from setup import erkenne_server, lade, speichere_geschützt, KONFIG, PASSWORT_DATEI

HINWEISE = {
    "gmail": "App-Passwort nötig: myaccount.google.com → Sicherheit → Bestätigung in zwei Schritten → App-Passwörter. Das normale Passwort funktioniert nicht.",
    "yahoo": "App-Passwort nötig: Yahoo Konto-Sicherheit → App-Passwort generieren. Das normale Passwort funktioniert nicht.",
    "outlook": "IMAP aktivieren in den Outlook-Einstellungen. Bei Microsoft-Konten ggf. App-Passwort nötig.",
    "gmx": "IMAP in den GMX-Einstellungen aktivieren. Meist reicht das normale Passwort.",
    "web.de": "IMAP in den web.de-Einstellungen aktivieren. Meist reicht das normale Passwort.",
    "freenet": "IMAP in den Freenet-Einstellungen aktivieren. Meist reicht das normale Passwort.",
}


def hinweis_für(domain, host):
    for schlüssel, text in HINWEISE.items():
        if schlüssel in domain or schlüssel in host:
            return text
    return "Prüfe, ob IMAP beim Anbieter aktiviert ist. Bei Problemen ein App-Passwort verwenden."


def mit_einfügen(feld):
    def einfügen(_=None):
        try:
            feld.insert(tk.INSERT, feld.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    menü = tk.Menu(feld, tearoff=0)
    menü.add_command(label="Einfügen", command=einfügen)

    def menü_zeigen(ereignis):
        menü.tk_popup(ereignis.x_root, ereignis.y_root)

    feld.bind("<Control-v>", einfügen)
    feld.bind("<Control-V>", einfügen)
    feld.bind("<Control-Shift-V>", einfügen)
    feld.bind("<Button-3>", menü_zeigen)
    feld.bind("<Button-2>", menü_zeigen)
    return feld


class Einrichtung:
    def __init__(self, wurzel):
        self.wurzel = wurzel
        self.wurzel.title("Mail-Reader einrichten")
        self.wurzel.geometry("560x640")
        self.wurzel.minsize(520, 560)
        self.rahmen = tk.Frame(wurzel, padx=20, pady=20)
        self.rahmen.pack(fill="both", expand=True)
        self.konten = json.loads(KONFIG.read_text(encoding="utf-8")) if KONFIG.exists() else []
        self.passwoerter = lade(PASSWORT_DATEI)
        self.server = None
        self.adresse_feld()

    def leeren(self):
        for kind in self.rahmen.winfo_children():
            kind.destroy()

    def adresse_feld(self):
        self.leeren()
        tk.Label(self.rahmen, text="E-Mail-Adresse", font=("", 12, "bold")).pack(anchor="w")
        self.adresse = mit_einfügen(tk.Entry(self.rahmen, width=45))
        self.adresse.pack(fill="x", pady=(4, 12))
        self.adresse.focus_set()
        self.adresse.bind("<Return>", lambda e: self.weiter())
        tk.Button(self.rahmen, text="Weiter", command=self.weiter).pack(anchor="e")
        self.status = tk.Label(self.rahmen, text=f"{len(self.konten)} Postfach/Postfächer eingerichtet", fg="gray")
        self.status.pack(anchor="w", pady=(20, 0))
        tk.Button(self.rahmen, text="Fertig", command=self.wurzel.destroy).pack(anchor="w", pady=(8, 0))

    def weiter(self):
        adresse = self.adresse.get().strip()
        if "@" not in adresse:
            messagebox.showerror("Ungültig", "Bitte eine gültige E-Mail-Adresse eingeben.")
            return
        domain = adresse.split("@", 1)[1].lower()
        self.server = erkenne_server(domain)
        self.adresse_wert = adresse
        self.passwort_feld(domain)

    def passwort_feld(self, domain):
        self.leeren()
        tk.Label(self.rahmen, text=self.adresse_wert, font=("", 12, "bold")).pack(anchor="w")
        zeile_server = tk.Frame(self.rahmen)
        zeile_server.pack(fill="x", anchor="w")
        tk.Label(zeile_server, text="IMAP-Server:").pack(side="left")
        self.host_feld = mit_einfügen(tk.Entry(zeile_server, width=30))
        self.host_feld.insert(0, self.server["host"])
        self.host_feld.pack(side="left", padx=(6, 0))
        tk.Label(self.rahmen, text=hinweis_für(domain, self.server["host"]), wraplength=420, justify="left", fg="#b35900").pack(anchor="w", pady=(10, 10))
        schlüssel = anbieter_schlüssel(self.server["host"])
        if schlüssel:
            anleitung = APP_PASSWORT_ANLEITUNG[schlüssel]
            tk.Label(self.rahmen, text=anleitung["titel"], font=("", 11, "bold")).pack(anchor="w")
            tk.Label(self.rahmen, text="\n".join(f"{n}. {t}" for n, t in enumerate(anleitung["schritte"], 1)),
                     wraplength=420, justify="left").pack(anchor="w", pady=(2, 6))
            tk.Button(self.rahmen, text="Seite im Browser öffnen", command=lambda: öffne_in_chrome(anleitung["url"])).pack(anchor="w", pady=(0, 10))
            öffne_in_chrome(anleitung["url"])
        tk.Label(self.rahmen, text="Passwort (App-Passwort, falls nötig)").pack(anchor="w")
        passwort_zeile = tk.Frame(self.rahmen)
        passwort_zeile.pack(fill="x", pady=(4, 12))
        self.passwort = mit_einfügen(tk.Entry(passwort_zeile, show="•", width=40))
        self.passwort.pack(side="left", fill="x", expand=True)
        self.auge = tk.Button(passwort_zeile, text="👁", width=3, command=self.passwort_umschalten)
        self.auge.pack(side="left", padx=(6, 0))
        self.passwort.focus_set()
        self.passwort.bind("<Return>", lambda e: self.speichern())
        zeile = tk.Frame(self.rahmen)
        zeile.pack(fill="x")
        tk.Button(zeile, text="Zurück", command=self.adresse_feld).pack(side="left")
        tk.Button(zeile, text="Testen und speichern", command=self.speichern).pack(side="right")

    def passwort_umschalten(self):
        verborgen = self.passwort.cget("show") == "•"
        self.passwort.config(show="" if verborgen else "•")

    def speichern(self):
        passwort = self.passwort.get()
        if not passwort:
            messagebox.showerror("Fehlt", "Bitte das Passwort eingeben.")
            return
        self.server["host"] = self.host_feld.get().strip() or self.server["host"]
        try:
            imap = imaplib.IMAP4_SSL(self.server["host"], self.server["port"], ssl_context=ssl.create_default_context())
            imap.login(self.adresse_wert, passwort)
            imap.logout()
        except Exception as fehler:
            messagebox.showerror("Anmeldung fehlgeschlagen", f"{fehler}\n\nPrüfe Passwort, App-Passwort und ob IMAP aktiviert ist.")
            return
        self.konten = [k for k in self.konten if k["user"] != self.adresse_wert]
        self.konten.append({"label": self.adresse_wert, "host": self.server["host"], "port": self.server["port"], "user": self.adresse_wert})
        self.passwoerter[self.adresse_wert] = passwort
        speichere_geschützt(KONFIG, self.konten)
        speichere_geschützt(PASSWORT_DATEI, self.passwoerter)
        messagebox.showinfo("Gespeichert", f"{self.adresse_wert} ist eingerichtet.")
        self.adresse_feld()


if __name__ == "__main__":
    wurzel = tk.Tk()
    Einrichtung(wurzel)
    wurzel.mainloop()
