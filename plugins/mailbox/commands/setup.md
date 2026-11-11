---
description: Postfächer einrichten (öffnet ein Fenster, in dem man E-Mail-Adresse und Passwort eingibt)
---

Starte das Einrichtungsfenster für mailbox, indem du diesen Befehl im Hintergrund ausführst:

```bash
nohup python3 "${CLAUDE_PLUGIN_ROOT}/setup_gui.py" >/dev/null 2>&1 &
```

Sag dem Nutzer danach kurz: Es ist ein Fenster geöffnet. Dort E-Mail-Adresse eingeben, auf „Weiter“ klicken, dann das Passwort (bei Gmail und Yahoo ein App-Passwort, die Schritte stehen im Fenster) eingeben und „Testen und speichern“ klicken. Danach einfach hier Bescheid sagen.

Falls das Fenster nicht erscheint, weil Tkinter fehlt, führe stattdessen im Hintergrund aus: `python3 "${CLAUDE_PLUGIN_ROOT}/setup.py"` und sag dem Nutzer, dass er die Fragen in dem Terminal beantworten muss, in dem Claude läuft, oder dass er `sudo apt install python3-tk` ausführen soll.
