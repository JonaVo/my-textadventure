def handle_level1_puzzle(command_text, session_data, rooms, items, npcs):
    """
    Verarbeitet Level-1-spezifische Rätsel. 
    Gibt zurück:
      (bool puzzle_handled, str message, int|None new_level, bool end_game)
    """
    words = command_text.split()
    verb = words[0] if len(words) > 0 else ""
    obj = words[1] if len(words) > 1 else ""
    current_room = session_data.get('current_room', 'start')
    inventory = session_data.get('inventory', [])
    got_code = session_data.get('got_code', False)

    # Beispiel: Truhe in Raum 'schuppen' öffnen
    # Spieler muss "benutze schlüssel auf truhe" eingeben,
    # wenn er sich im 'schuppen' befindet.
    if verb == "benutze" and len(words) == 4 and words[2] == "auf":
        target = words[3]
        if target == "truhe" and current_room == "schuppen":
            if "schlüssel" in inventory and got_code:
                # Sobald die Truhe in Level 1 geöffnet wird, ist das Spiel zu Ende.
                message = (
                    "Du hast die Truhe geöffnet! Darin findest du Vorräte und ein altes Buch. "
                    "Ein helles Licht blendet dich ... Du hast das Spiel beendet!"
                )
                # puzzle_handled=True, message=..., new_level=None, end_game=True
                return True, message, None, True
            else:
                # Schlüssel oder Code fehlt
                message = "Dir fehlt entweder der Schlüssel oder der Code."
                return True, message, None, False

    # Kein Puzzle erkannt
    return False, "", None, False