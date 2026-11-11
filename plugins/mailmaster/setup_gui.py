#!/usr/bin/env python3
"""Einrichtungsfenster für mailmaster im Jarvis-Stil."""

import imaplib
import json
import ssl
import tkinter as tk
from tkinter import messagebox

from anleitung import anbieter_schlüssel, anleitung, öffne_in_chrome
from i18n import t
from geheimnisse import keyring_installieren, keyring_verfügbar, passwort_löschen, passwort_speichern
from setup import erkenne_server, speichere_geschützt, KONFIG

BG = "#050b14"
PANEL = "#0d1b2e"
FG = "#eaf6ff"
MUTED = "#7fb3d5"
ACCENT = "#00d4ff"
ACCENT_HELL = "#5be8ff"
GREEN = "#4dffb8"
RED = "#ff6b6b"
EINGABE = "#020610"
RAHMEN = "#123246"
SCHRIFT = ("Sans", 10)
SCHRIFT_FETT = ("Sans", 10, "bold")


def knopf(eltern, text, befehl, akzent=False, farbe=None):
    if akzent:
        return tk.Button(eltern, text=text, command=befehl, bg=ACCENT, fg="#00131a",
                         activebackground=ACCENT_HELL, activeforeground="#00131a",
                         relief="flat", padx=16, pady=8, font=SCHRIFT_FETT, cursor="hand2")
    return tk.Button(eltern, text=text, command=befehl, bg=PANEL, fg=farbe or MUTED,
                     activebackground=RAHMEN, activeforeground=ACCENT,
                     relief="flat", padx=12, pady=6, font=SCHRIFT, cursor="hand2")


def eingabe(eltern, breite=40, verborgen=False):
    return tk.Entry(eltern, width=breite, bg=EINGABE, fg=ACCENT_HELL, insertbackground=ACCENT_HELL,
                    relief="flat", font=("Monospace", 10), highlightthickness=1,
                    highlightbackground=RAHMEN, highlightcolor=ACCENT,
                    show="•" if verborgen else "")


def mit_einfügen(feld):
    def einfügen(_=None):
        try:
            feld.insert(tk.INSERT, feld.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    menü = tk.Menu(feld, tearoff=0, bg=PANEL, fg=FG, activebackground=RAHMEN, activeforeground=ACCENT)
    menü.add_command(label="Einfügen", command=einfügen)

    def menü_zeigen(ereignis):
        menü.tk_popup(ereignis.x_root, ereignis.y_root)

    feld.bind("<Control-v>", einfügen)
    feld.bind("<Control-V>", einfügen)
    feld.bind("<Control-Shift-V>", einfügen)
    feld.bind("<Button-3>", menü_zeigen)
    feld.bind("<Button-2>", menü_zeigen)
    return feld


def hinweis_für(host):
    schlüssel = anbieter_schlüssel(host)
    return anleitung(schlüssel) if schlüssel else None


class Einrichtung:
    def __init__(self, wurzel):
        self.wurzel = wurzel
        self.wurzel.title(t("app_title"))
        self.wurzel.geometry("600x700")
        self.wurzel.minsize(560, 600)
        self.wurzel.configure(bg=BG)
        self.rahmen = tk.Frame(wurzel, bg=BG, padx=24, pady=20)
        self.rahmen.pack(fill="both", expand=True)
        self.konten = json.loads(KONFIG.read_text(encoding="utf-8")) if KONFIG.exists() else []
        self.server = None
        self.adresse_wert = ""
        self.adresse_feld()

    def kopf(self, untertitel):
        tk.Label(self.rahmen, text="✨ " + t("app_title"), font=("Sans", 18, "bold"),
                 bg=BG, fg=ACCENT).pack(anchor="w")
        tk.Label(self.rahmen, text=untertitel, bg=BG, fg=MUTED, font=SCHRIFT).pack(anchor="w", pady=(2, 14))

    def leeren(self):
        for kind in self.rahmen.winfo_children():
            kind.destroy()

    def adresse_feld(self):
        self.leeren()
        self.kopf(t("header_add"))
        karte = tk.Frame(self.rahmen, bg=PANEL, padx=16, pady=14)
        karte.pack(fill="x")
        tk.Label(karte, text=t("label_address"), bg=PANEL, fg=FG, font=SCHRIFT_FETT).pack(anchor="w")
        self.adresse = mit_einfügen(eingabe(karte, 50))
        self.adresse.pack(fill="x", pady=(6, 12), ipady=4)
        self.adresse.focus_set()
        self.adresse.bind("<Return>", lambda e: self.weiter())
        knopf(karte, t("btn_next"), self.weiter, akzent=True).pack(anchor="e")

        tk.Label(self.rahmen, text=t("count", n=len(self.konten)), bg=BG, fg=FG,
                 font=SCHRIFT_FETT).pack(anchor="w", pady=(18, 6))
        liste = tk.Frame(self.rahmen, bg=PANEL, padx=10, pady=6)
        liste.pack(fill="x")
        if not self.konten:
            tk.Label(liste, text=t("label_none"), bg=PANEL, fg=MUTED, font=SCHRIFT).pack(anchor="w", pady=4)
        for konto in self.konten:
            zeile = tk.Frame(liste, bg=PANEL)
            zeile.pack(fill="x", pady=2)
            tk.Label(zeile, text="●", bg=PANEL, fg=GREEN, font=SCHRIFT).pack(side="left", padx=(0, 8))
            tk.Label(zeile, text=f"{konto['user']}   {konto['host']}", bg=PANEL, fg=FG, font=("Monospace", 9),
                     anchor="w").pack(side="left", fill="x", expand=True)
            knopf(zeile, t("btn_delete"), lambda k=konto: self.konto_löschen(k), farbe=RED).pack(side="right")

        knopf(self.rahmen, t("btn_done"), self.wurzel.destroy).pack(anchor="e", pady=(18, 0))

    def konto_löschen(self, konto):
        if not messagebox.askyesno(t("del_title"), t("del_text", adresse=konto["user"])):
            return
        self.konten = [k for k in self.konten if k["user"] != konto["user"]]
        try:
            passwort_löschen(konto["user"])
        except Exception as fehler:
            messagebox.showerror(t("kr_title"), f"{t('kr_failed')}\n\n{fehler}")
            return
        speichere_geschützt(KONFIG, self.konten)
        self.adresse_feld()

    def weiter(self):
        adresse = self.adresse.get().strip()
        if "@" not in adresse:
            messagebox.showerror(t("err_invalid_title"), t("err_invalid_text"))
            return
        domain = adresse.split("@", 1)[1].lower()
        self.server = erkenne_server(domain)
        self.adresse_wert = adresse
        self.passwort_feld()

    def passwort_feld(self):
        self.leeren()
        self.kopf(self.adresse_wert)
        karte = tk.Frame(self.rahmen, bg=PANEL, padx=16, pady=14)
        karte.pack(fill="x")

        server_zeile = tk.Frame(karte, bg=PANEL)
        server_zeile.pack(fill="x")
        tk.Label(server_zeile, text=t("label_server"), bg=PANEL, fg=FG, font=SCHRIFT_FETT).pack(side="left")
        self.host_feld = mit_einfügen(eingabe(server_zeile, 32))
        self.host_feld.insert(0, self.server["host"])
        self.host_feld.pack(side="left", padx=(12, 0), ipady=3)

        anleitung_daten = hinweis_für(self.server["host"])
        if anleitung_daten:
            tk.Label(karte, text=anleitung_daten["titel"], bg=PANEL, fg=ACCENT, font=SCHRIFT_FETT).pack(anchor="w", pady=(14, 4))
            for nummer, schritt in enumerate(anleitung_daten["schritte"], 1):
                tk.Label(karte, text=f"{nummer}.  {schritt}", bg=PANEL, fg=MUTED, font=SCHRIFT,
                         wraplength=480, justify="left").pack(anchor="w", pady=1)
            knopf(karte, t("btn_open_chrome"), lambda: öffne_in_chrome(anleitung_daten["url"])).pack(anchor="w", pady=(8, 0))
            öffne_in_chrome(anleitung_daten["url"])

        tk.Label(karte, text=t("label_password"), bg=PANEL, fg=FG, font=SCHRIFT_FETT).pack(anchor="w", pady=(16, 6))
        passwort_zeile = tk.Frame(karte, bg=PANEL)
        passwort_zeile.pack(fill="x")
        self.passwort = mit_einfügen(eingabe(passwort_zeile, 40, verborgen=True))
        self.passwort.pack(side="left", fill="x", expand=True, ipady=4)
        self.auge = knopf(passwort_zeile, "👁", self.passwort_umschalten)
        self.auge.pack(side="left", padx=(8, 0))
        self.passwort.focus_set()
        self.passwort.bind("<Return>", lambda e: self.speichern())

        zeile = tk.Frame(self.rahmen, bg=BG)
        zeile.pack(fill="x", pady=(18, 0))
        knopf(zeile, t("btn_back"), self.adresse_feld).pack(side="left")
        knopf(zeile, t("btn_save"), self.speichern, akzent=True).pack(side="right")

    def passwort_umschalten(self):
        verborgen = self.passwort.cget("show") == "•"
        self.passwort.config(show="" if verborgen else "•")

    def speichern(self):
        passwort = self.passwort.get()
        if not passwort:
            messagebox.showerror(t("err_missing_title"), t("err_missing_text"))
            return
        self.server["host"] = self.host_feld.get().strip() or self.server["host"]
        try:
            imap = imaplib.IMAP4_SSL(self.server["host"], self.server["port"], ssl_context=ssl.create_default_context())
            imap.login(self.adresse_wert, passwort)
            imap.logout()
        except Exception as fehler:
            messagebox.showerror(t("err_login_title"), t("err_login_text", error=fehler))
            return
        if not keyring_verfügbar():
            if not (messagebox.askyesno(t("kr_title"), t("kr_text")) and keyring_installieren()):
                messagebox.showerror(t("kr_title"), t("kr_failed"))
                return
        passwort_speichern(self.adresse_wert, passwort)
        self.konten = [k for k in self.konten if k["user"] != self.adresse_wert]
        self.konten.append({"label": self.adresse_wert, "user": self.adresse_wert, **self.server})
        speichere_geschützt(KONFIG, self.konten)
        messagebox.showinfo(t("ok_title"), t("ok_text", adresse=self.adresse_wert))
        self.adresse_feld()


if __name__ == "__main__":
    wurzel = tk.Tk()
    Einrichtung(wurzel)
    wurzel.mainloop()
