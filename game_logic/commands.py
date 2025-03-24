from flask import session, redirect

def process_command(command_text, session_data, rooms, items, npcs):
    """
    Verarbeitet den Befehl und enthält Logik für:
    - Altes Truhenrätsel (Raum 'schuppen')
    - Neues Waffensystem (Teile sammeln, Mechaniker baut Waffe)
    - Monster-Areal (Raum 'monsterarena')

    Gibt zurück:
    - message (str)
    - new_level (int oder None)
    - end_game (bool)
    """
    words = command_text.split()
    verb = words[0] if len(words) > 0 else ""
    obj = words[1] if len(words) > 1 else ""

    current_room = session_data.get('current_room', 'start')
    inventory = session_data.get('inventory', [])

    # Wurde der Code für die Truhe gelernt?
    got_code = session_data.get('got_code', False)
    # Ist die Waffe für das Monster fertig?
    waffe_fertig = session_data.get('waffe_fertig', False)

    message = ""
    error = ""
    new_level = None
    end_game = False
    won_game = False

    # 1) Bewegung
    if verb in rooms[current_room]:
        next_room = rooms[current_room][verb]

        # Spezialfall: Monsterarena
        if next_room == "monsterarena":
            if not waffe_fertig:
                # Ohne fertige Waffe -> Game Over
                message = (
                    "Du betrittst die Arena ... ein unheimliches Brüllen ertönt. "
                    "Ohne Waffe hast du keine Chance! Das Monster reißt dich in Stücke.\n"
                    "Das Spiel ist beendet!"
                )
                end_game = True
                won_game = False
            else:
                # Mit fertiger Waffe -> Sieg
                message = (
                    "Bewaffnet betrittst du die Arena. Das Monster greift an, "
                    "doch du bist bereit. Mit einem letzten Schuss besiegst du es!\n"
                    "Du hast das Spiel erfolgreich beendet!"
                )
                end_game = True
                won_game = True
                session['level'] = session['level'] +1
            return message, error, new_level, end_game, won_game

        # Normaler Raumwechsel
        session_data['current_room'] = next_room
        message = f"Du gehst nach {verb}."
        return message, error, new_level, end_game, won_game

    # 2) Nimm
    if verb == 'nimm':
        if obj in items and items[obj]['location'] == current_room and items[obj]['pickupable']:
            inventory.append(obj)
            session_data['inventory'] = inventory
            items[obj]['location'] = 'inventory'
            message = f"Du hebst den {obj} auf."
        else:
            message = f"Du kannst '{obj}' hier nicht aufnehmen."
        return message, error, new_level, end_game, won_game

    # 3) Untersuche
    if verb == 'untersuche':
        if obj in items:
            # Prüfen, ob das Item im aktuellen Raum oder im Inventar ist
            if items[obj]['location'] in [current_room, 'inventory']:
                message = f"Du untersuchst {obj}: {items[obj]['description']}"
                if obj == "truhencode":
                    session_data['got_code'] = True
            else:
                message = f"Hier ist kein '{obj}' zum Untersuchen."

        elif obj in npcs:
            # NPC untersuchen
            if npcs[obj]['location'] == current_room:
                message = f"Du betrachtest {obj} genauer. Er wirkt erschöpft, aber freundlich."
            else:
                message = f"'{obj}' ist nicht hier."
        else:
            message = f"Du findest nichts Interessantes zu '{obj}'."

        return message, error, new_level, end_game, won_game

    # 4) Rede mit ...
    if verb == 'rede':
        # Syntax: 'rede mit <person>'
        if len(words) >= 3 and words[1] == 'mit':
            person = words[2]
            if person in npcs and npcs[person]['location'] == current_room:
                dialogue_lines = npcs[person]['dialogue']
                message = "\n".join(dialogue_lines)

                # Falls Gespräch Code für die Truhe verrät
                session_data['got_code'] = True

                # Check, ob es der Mechaniker ist, der die Waffe bauen kann
                if person == 'mechaniker':
                    # Liste der benötigten Teile
                    benoetigte_teile = [
                        "stahlrohr", 
                        "abzugseinheit", 
                        "energiezelle", 
                        "spezialkleber", 
                        "schweissgeraet"
                    ]

                    if "waffe" in inventory:
                        # Spieler hat die Waffe bereits
                        message += (
                            "\n\nDer Mechaniker mustert dich: "
                            "»Du hast ja schon die Waffe! "
                            "Verschwende keine Zeit und erledige das Monster!«"
                        )
                    else:
                        # Prüfe, ob alle Teile im Inventar sind
                        if all(teil in inventory for teil in benoetigte_teile):
                            session_data['waffe_fertig'] = True
                            # Entferne die Teile aus dem Inventar
                            for teil in benoetigte_teile:
                                inventory.remove(teil)

                            # Lege die neue Waffe ins Inventar
                            inventory.append("waffe")
                            # Falls du möchtest, dass man "untersuche waffe" machen kann:
                            items["waffe"] = {
                                "name": "waffe",
                                "description": (
                                    "Eine zusammengebaute Waffe, stark genug "
                                    "um das Monster zu töten."
                                ),
                                "location": "inventory",
                                "pickupable": True
                            }

                            message += (
                                "\n\nDer Mechaniker grinst: »Du hast ja alles! "
                                "Dann leg ich mal los...«\n"
                                "Nach einiger Zeit hältst du eine funktionierende Waffe in Händen.\n"
                                "»Jetzt kannst du das Monster besiegen!«"
                            )
                        else:
                            message += (
                                "\n\n»Dir fehlen noch Teile, um die Waffe zusammenzubauen. "
                                "Bring mir alles, dann helfe ich dir.«"
                            )
            else:
                message = f"'{person}' ist nicht hier."
        else:
            message = "Mit wem möchtest du reden? Beispiel: 'rede mit mechaniker'"

        return message, error, new_level, end_game, won_game

    # 5) Benutze ...
    if verb == 'benutze':
        # Spieler muss "benutze <item> auf <ziel>" eingeben
        if len(words) == 4 and words[2] == 'auf':
            target = words[3]
            # Altes Truhenrätsel: In Raum 'schuppen', 'benutze schlüssel auf truhe'
            if target == 'truhe' and current_room == 'schuppen':
                if 'schlüssel' in inventory and got_code:
                    message = (
                        "Du hast die Truhe geöffnet! Darin findest du Vorräte und ein altes Buch. "
                        "Ein helles Licht blendet dich ... Du hast das Level beendet!"
                    )
                    end_game = True
                    won_game = True
                    session['level'] = session['level'] +1  # Spielende
                else:
                    message = "Dir fehlt entweder der Schlüssel oder der Code."
                return message, error, new_level, end_game, won_game

            # Beispiel: Weitere Rätsel möglich ("benutze gasmaske auf chemielabor" etc.)
            # if target == 'chemielabor' and obj == 'gasmaske':
            #     ...
            #     return message, new_level, end_game

        # Falls kein Rätsel getriggert wird, kann man hier optional eine Standardaktion einbauen
        message = "Nichts passiert ..."
        return message, error, new_level, end_game, won_game

    # 6) Inventar
    if verb == 'inventar':
        if inventory:
            message = "Dein Inventar enthält: " + ", ".join(inventory)
        else:
            message = "Dein Inventar ist leer."
        return message, error, new_level, end_game, won_game

    # 7) Ungültiger Befehl
    possible_commands = [key for key in rooms[current_room].keys() if key != "description"]
    possible_commands += ["nimm <item>", "untersuche <objekt>", "rede mit <person>", "benutze <item> auf <ziel>", "inventar"]
    error = "Ungültiger Befehl. Versuche es mit: " + ", ".join(possible_commands)
    return message, error, new_level, end_game, won_game