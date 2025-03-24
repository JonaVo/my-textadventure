# game_data/level2_data.py

"""
Level 2 Data:
Eine verlassene Fabrik mit mehreren Räumen. Du musst eine Waffe aus Einzelteilen
zusammensetzen (der Mechaniker hilft dir), um ein Monster zu besiegen.
"""

rooms_level2 = {
    "start": {
        "description": (
            "Du betrittst den verlassenen Fabrikhof. Rostige Zäune und Unkraut "
            "überall. In der Ferne ragen die Überreste von Werkshallen auf.\n\n"
            "Ausgänge: osten (Kontrollraum), norden (Werkhalle)"
        ),
        "osten": "kontrollraum",
        "norden": "werkhalle"
    },
    "kontrollraum": {
        "description": (
            "Du stehst in einem kleinen Kontrollraum. Ein alter Mechaniker hat sich "
            "hier verbarrikadiert. Überall flackern defekte Monitore.\n\n"
            "Ausgänge: westen (zurück zum Fabrikhof), süden (Chemielabor)"
        ),
        "westen": "start",
        "süden": "chemielabor"
    },
    "werkhalle": {
        "description": (
            "Eine riesige Werkhalle mit kaputten Förderbändern und "
            "zertrümmerten Maschinen. Es riecht nach Öl und Staub.\n\n"
            "Ausgänge: süden (Fabrikhof), osten (Lagerhalle)"
        ),
        "süden": "start",
        "osten": "lagerhalle"
    },
    "chemielabor": {
        "description": (
            "Das alte Chemielabor ist teilweise eingestürzt. Zersplitterte Reagenzgläser "
            "und rostige Apparaturen liegen herum. Ein beißender Geruch von Chemikalien "
            "liegt in der Luft.\n\n"
            "Ausgänge: norden (Kontrollraum), osten (Lagerhalle)"
        ),
        "norden": "kontrollraum",
        "osten": "lagerhalle"
    },
    "lagerhalle": {
        "description": (
            "Du betrittst eine dunkle Lagerhalle, in der Kisten und Regale "
            "durcheinandergeworfen wurden. Ein unheimliches Echo hallt "
            "zwischen den Wänden.\n\n"
            "Ausgänge: westen (Werkhalle), westen2 (Chemielabor), norden (monsterarena)"
            "\n(Hinweis: Hier musst du vielleicht \"westen\" oder \"westen2\" eingeben, "
            "je nach Raum, den du ansteuern willst.)"
        ),
        "westen": "werkhalle",  # oder z. B. "werkhalle_eingang"
        "westen2": "chemielabor",
        "norden": "monsterarena"
    },
    "monsterarena": {
        "description": (
            "Ein riesiger, abgetrennter Bereich der Fabrik. Im Halbdunkel "
            "siehst du einen unheimlichen Schatten – das Monster!\n\n"
            "Ausgänge: süden (zurück zur Lagerhalle)"
        ),
        "süden": "lagerhalle"
    }
}

items_level2 = {
    # Teile für die Waffe
    "stahlrohr": {
        "name": "stahlrohr",
        "description": (
            "Ein massives Stahlrohr, das als Lauf für eine Waffe dienen könnte."
        ),
        "location": "werkhalle",  # Findest du in der Werkhalle
        "pickupable": True
    },
    "abzugseinheit": {
        "name": "abzugseinheit",
        "description": (
            "Ein Abzug und ein kleiner Mechanismus. Könnte Teil einer Schusswaffe sein."
        ),
        "location": "lagerhalle",  # Liegt in einer Kiste in der Lagerhalle
        "pickupable": True
    },
    "energiezelle": {
        "name": "energiezelle",
        "description": (
            "Eine kleine Energiezelle, die Strom für eine futuristische Waffe liefert."
        ),
        "location": "chemielabor",  # Musst du im Labor bergen
        "pickupable": True
    },
    "spezialkleber": {
        "name": "spezialkleber",
        "description": (
            "Ein hochfester Klebstoff, um Metallteile miteinander zu verbinden."
        ),
        "location": "chemielabor",
        "pickupable": True
    },
    # Werkzeug, das der Mechaniker zum Zusammenbauen braucht
    "schweissgeraet": {
        "name": "schweißgerät",
        "description": (
            "Ein tragbares Schweißgerät. Der Mechaniker braucht es, "
            "um die Waffe zusammenzusetzen."
        ),
        "location": "werkhalle",
        "pickupable": True
    },
    # Optional: Gasmaske oder Schlüssel
    "gasmaske": {
        "name": "gasmaske",
        "description": (
            "Eine Gasmaske, die dich vor giftigen Dämpfen schützt."
        ),
        "location": "kontrollraum",
        "pickupable": True
    },
    "waffe": {
        "name": "waffe",
        "description": (
            "Eine zusammengebaute Waffe, stark genug "
            "um das Monster zu töten."
        ),
        "location": "none",  # Noch nicht im Raum
        "pickupable": False
    }
}

npcs_level2 = {
    # Mechaniker, der die Waffe reparieren kann
    "mechaniker": {
        "name": "mechaniker",
        "dialogue": [
            "Der Mechaniker nickt dir zu: »Bist du verrückt? Hier haust ein Monster!«",
            "Er seufzt: »Wenn du eine Waffe brauchst, besorg mir die Teile: "
            "einen Lauf (stahlrohr), eine Abzugseinheit, eine Energiezelle und "
            "etwas zum Verbinden. Ach, und ein Schweißgerät wäre hilfreich.«",
            "»Bring mir alles, dann kann ich dir eine Waffe bauen. Sonst wirst du "
            "das Monster nicht besiegen können!«"
        ],
        "location": "kontrollraum"
    },
    # Beispiel-NPC: Forscher
    "forscher": {
        "name": "forscher",
        "dialogue": [
            "Der Forscher schaut nervös um sich: »Ich war hier, um die alten "
            "Chemikalien zu untersuchen, aber irgendwas stimmt nicht ...«",
            "»Ich habe dieses unheimliche Brüllen gehört. Ich fürchte, es ist "
            "mehr als nur ein Tier.«",
            "»Pass auf dich auf, Fremder. Ohne Waffe hast du keine Chance.«"
        ],
        "location": "chemielabor"
    },
    # Monster als spezieller NPC (falls du es so umsetzen willst)
    "monster": {
        "name": "monster",
        "dialogue": [
            "Ein tiefes Knurren ertönt aus der Dunkelheit ...",
            "Das Monster stößt ein markerschütterndes Brüllen aus."
        ],
        "location": "monsterarena"
    }
}