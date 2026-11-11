"""Bestätigungsfenster vor dem Versand, im Jarvis-Stil. Nur der Nutzer kann hier Ja klicken."""

import tkinter as tk

from i18n import t

BG = "#050b14"
PANEL = "#0d1b2e"
FG = "#eaf6ff"
MUTED = "#7fb3d5"
ACCENT = "#00d4ff"
ACCENT_HELL = "#5be8ff"
RED = "#ff6b6b"
EINGABE = "#020610"
RAHMEN = "#123246"


def nutzer_bestätigt(von, an, betreff, text):
    try:
        wurzel = tk.Tk()
    except tk.TclError:
        return False
    wurzel.title(t("send_title"))
    wurzel.configure(bg=BG)
    wurzel.geometry("560x520")
    wurzel.minsize(520, 480)
    wurzel.attributes("-topmost", True)
    entschieden = {"ja": False}

    def ja():
        entschieden["ja"] = True
        wurzel.destroy()

    def nein():
        wurzel.destroy()

    rahmen = tk.Frame(wurzel, bg=BG, padx=24, pady=20)
    rahmen.pack(fill="both", expand=True)
    tk.Label(rahmen, text="✨ J.A.R.V.I.S.", font=("Sans", 16, "bold"), bg=BG, fg=ACCENT).pack(anchor="w")
    tk.Label(rahmen, text=t("send_question"), font=("Sans", 12, "bold"), bg=BG, fg=FG).pack(anchor="w", pady=(4, 12))

    karte = tk.Frame(rahmen, bg=PANEL, padx=16, pady=12)
    karte.pack(fill="x")
    for beschriftung, wert in ((t("send_from"), von), (t("send_to"), an), (t("send_subject"), betreff)):
        zeile = tk.Frame(karte, bg=PANEL)
        zeile.pack(fill="x", pady=2)
        tk.Label(zeile, text=f"{beschriftung}:", width=10, anchor="w", bg=PANEL, fg=MUTED, font=("Sans", 10, "bold")).pack(side="left")
        tk.Label(zeile, text=wert, anchor="w", bg=PANEL, fg=FG, font=("Monospace", 10)).pack(side="left", fill="x", expand=True)

    tk.Label(rahmen, text=t("send_body"), bg=BG, fg=MUTED, font=("Sans", 10, "bold")).pack(anchor="w", pady=(14, 4))
    textfeld = tk.Text(rahmen, height=10, wrap="word", bg=EINGABE, fg="#5be8ff", relief="flat",
                       font=("Monospace", 10), padx=10, pady=8, highlightthickness=1,
                       highlightbackground=RAHMEN, highlightcolor=ACCENT)
    textfeld.insert("1.0", text)
    textfeld.config(state="disabled")
    textfeld.pack(fill="both", expand=True)

    knöpfe = tk.Frame(rahmen, bg=BG)
    knöpfe.pack(fill="x", pady=(16, 0))
    tk.Button(knöpfe, text=t("send_no"), command=nein, bg=PANEL, fg=RED, activebackground="#2a1418",
              activeforeground=RED, relief="flat", padx=16, pady=8, font=("Sans", 10, "bold"),
              cursor="hand2").pack(side="left")
    tk.Button(knöpfe, text=t("send_yes"), command=ja, bg=ACCENT, fg="#00131a", activebackground=ACCENT_HELL,
              activeforeground="#00131a", relief="flat", padx=20, pady=8, font=("Sans", 10, "bold"),
              cursor="hand2").pack(side="right")
    wurzel.bind("<Escape>", lambda e: nein())
    wurzel.protocol("WM_DELETE_WINDOW", nein)
    wurzel.mainloop()
    return entschieden["ja"]
