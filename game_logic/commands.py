from flask import session, redirect

def process_command(command_text, session_data, rooms, items, npcs):
    """
    Verarbeitet den Befehl und führt das Truhenrätsel aus.
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
    got_code = session_data.get('got_code', False)

    message = ""
    new_level = None
    end_game = False

    # 1) Bewegung
    if verb in rooms[current_room]:
        session_data['current_room'] = rooms[current_room][verb]
        message = f"Du gehst nach {verb}."
        return message, new_level, end_game

    # 2) Nimm
    if verb == 'nimm':
        if obj in items and items[obj]['location'] == current_room and items[obj]['pickupable']:
            inventory.append(obj)
            session_data['inventory'] = inventory
            items[obj]['location'] = 'inventory'
            message = f"Du hebst den {obj} auf."
        else:
            message = f"Du kannst '{obj}' hier nicht aufnehmen."
        return message, new_level, end_game

    # 3) Untersuche
    if verb == 'untersuche':
        if obj in items:
            # Prüfen, ob das Item im aktuellen Raum oder im Inventar ist
            if items[obj]['location'] in [current_room, 'inventory']:
                message = f"Du untersuchst {obj}: {items[obj]['description']}"
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

        return message, new_level, end_game

    # 4) Rede mit ...
    if verb == 'rede':
        # Syntax: 'rede mit wanderer'
        if len(words) >= 3 and words[1] == 'mit':
            person = words[2]
            if person in npcs and npcs[person]['location'] == current_room:
                dialogue_lines = npcs[person]['dialogue']
                message = "\n".join(dialogue_lines)
                # Wenn das Gespräch den Code verrät, setze got_code auf True
                session_data['got_code'] = True
            else:
                message = f"'{person}' ist nicht hier."
        else:
            message = "Mit wem möchtest du reden? Beispiel: 'rede mit wanderer'"

        return message, new_level, end_game

    # 5) Benutze ... (direkt das Truhenrätsel einbauen)
    if verb == 'benutze':
        # Spieler muss "benutze <item> auf <ziel>" eingeben
        if len(words) == 4 and words[2] == 'auf':
            target = words[3]
            # Truhenrätsel: In Raum 'schuppen', 'benutze schlüssel auf truhe'
            if target == 'truhe' and current_room == 'schuppen':
                if 'schlüssel' in inventory and got_code:
                    message = (
                        "Du hast die Truhe geöffnet! Darin findest du Vorräte und ein altes Buch. "
                        "Ein helles Licht blendet dich ... Du hast das Spiel beendet!"
                    )
                    end_game = True  # Spielende
                else:
                    message = "Dir fehlt entweder der Schlüssel oder der Code."
                return message, new_level, end_game
        # Falls kein Rätsel getriggert wird, kann man hier optional eine Standardaktion einbauen
        pass

    # 6) Inventar
    if verb == 'inventar':
        if inventory:
            message = "Dein Inventar enthält: " + ", ".join(inventory)
        else:
            message = "Dein Inventar ist leer."
        return message, new_level, end_game

    # 7) Ungültiger Befehl
    possible_commands = [key for key in rooms[current_room].keys() if key != "description"]
    possible_commands += ["nimm <item>", "untersuche <objekt>", "rede mit <person>", "benutze <item> auf <ziel>", "inventar"]
    message = "Ungültiger Befehl. Versuche es mit: " + ", ".join(possible_commands)
    return message, new_level, end_game