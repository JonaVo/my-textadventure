from flask import session, redirect

# Hier importieren wir die Level-spezifischen Puzzle-Funktionen
from game_logic.level1_logic import handle_level1_puzzle
from game_logic.level2_logic import handle_level2_puzzle

def process_command(command_text, session_data, rooms, items, npcs):
    """
    Verarbeitet den Befehl und ruft ggf. level-spezifische Logik auf.
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
    level = session_data.get('level', 1)

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
                # Beispiel: Wenn das Gespräch den Code verrät, setze got_code auf True
                session_data['got_code'] = True
            else:
                message = f"'{person}' ist nicht hier."
        else:
            message = "Mit wem möchtest du reden? Beispiel: 'rede mit wanderer'"

        return message, new_level, end_game

    # 5) Benutze ...
    if verb == 'benutze':
        # Bevor wir den Standard abhandeln, schauen wir, ob es level-spezifische Puzzle gibt
        puzzle_handled, puzzle_message, puzzle_new_level, puzzle_end_game = handle_level_specific(
            level, command_text, session_data, rooms, items, npcs
        )
        if puzzle_handled:
            return puzzle_message, puzzle_new_level, puzzle_end_game

        # Falls das Puzzle nicht vom Level-Handler verarbeitet wurde,
        # machen wir hier Standardaktionen ...
        # ...
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


def handle_level_specific(level, command_text, session_data, rooms, items, npcs):
    """
    Ruft je nach Level die passende Puzzle-Funktion auf.
    """
    if level == 1:
        return handle_level1_puzzle(command_text, session_data, rooms, items, npcs)
    elif level == 2:
        return handle_level2_puzzle(command_text, session_data, rooms, items, npcs)

    # Keine spezielle Logik
    return False, "", None, False