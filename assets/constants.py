# Räume des Spiels
rooms = {
    "start": {
        "description": (
            "Du wachst in einem notdürftig eingerichteten Unterschlupf auf. "
            "Draußen siehst du eine verlassene Siedlung. "
            "Du hörst in der Ferne das Fauchen des Windes und erkennst die Trümmer einer alten Tankstelle."
            "\n\nAusgänge: norden (Siedlung), osten (Tankstelle)"
        ),
        "norden": "siedlung",
        "osten": "tankstelle"
    },
    "siedlung": {
        "description": (
            "Du befindest dich in den Ruinen einer alten Wohnsiedlung. "
            "Einige Häuser stehen noch, aber die meisten sind eingestürzt. "
            "Am Straßenrand sitzt ein Wanderer in zerlumpten Kleidern, der dich aufmerksam mustert."
            "\n\nAusgänge: süden (zurück zum Unterschlupf), westen (Waldpfad)"
        ),
        "süden": "start",
        "westen": "waldpfad"
    },
    "tankstelle": {
        "description": (
            "Die alte Tankstelle ist halb eingestürzt. In einer Ecke steht ein verrosteter Automat. "
            "Der Boden ist von Trümmern bedeckt. Vielleicht findest du hier etwas Nützliches."
            "\n\nAusgänge: westen (zurück zum Unterschlupf)"
        ),
        "westen": "start"
    },
    "waldpfad": {
        "description": (
            "Ein schmaler Pfad führt in einen dichten Wald. Die Bäume sind kahl und es riecht nach Moder. "
            "Zwischen den Stämmen erkennst du einen alten Schuppen."
            "\n\nAusgänge: osten (Siedlung), norden (schuppen)"
        ),
        "osten": "siedlung",
        "norden": "schuppen"
    },
    "schuppen": {
        "description": (
            "Du stehst vor einem baufälligen Schuppen. Die Tür ist angelehnt. "
            "Im Inneren erkennst du eine alte Truhe, die scheinbar verschlossen ist."
            "\n\nAusgänge: süden (zurück zum Waldpfad)"
        ),
        "süden": "waldpfad"
    }
}

# Gegenstände des Spiels
items = {
    "schlüssel": {
        "name": "schlüssel",
        "description": "Ein rostiger Schlüssel, der schon bessere Tage gesehen hat.",
        "location": "tankstelle",     # Wo er zu finden ist
        "pickupable": True,           # Kann der Spieler ihn aufheben?
    },
    "truhencode": {
        "name": "truhencode",
        "description": "Auf einem Zettel steht eine vierstellige Zahl: 4711.",
        "location": "siedlung",       # Bekommt man nur durch Gespräch mit Wanderer (oder man findet ihn?)
        "pickupable": False           # Wird durch Dialog 'verraten', nicht physisch aufgehoben
    }
}

# NPCs (Nicht-Spieler-Charaktere)
npcs = {
    "wanderer": {
        "name": "wanderer",
        "dialogue": [
            "Der Wanderer schaut dich an: »Du suchst wohl nach etwas Wertvollem?«",
            "Er fährt fort: »Ich habe Gerüchte über eine verschlossene Truhe in einem alten Schuppen gehört. "
            "Vielleicht öffnet sie sich mit dem Code 4711...«",
            "Er lächelt müde: »Aber sei vorsichtig, in dieser Welt lauern überall Gefahren.«"
        ],
        "location": "siedlung"  # Der Wanderer ist in der Siedlung
    }
}
