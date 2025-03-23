# game_logic/level2_logic.py

def handle_level2_puzzle(command_text, session_data, rooms, items, npcs):
    """
    Verarbeitet Level-2-spezifische Rätsel.
    Gibt zurück:
      (bool puzzle_handled, str message, int|None new_level, bool end_game)
    """
    words = command_text.split()
    verb = words[0] if len(words) > 0 else ""
    obj = words[1] if len(words) > 1 else ""
    current_room = session_data.get('current_room', 'start')

    # Beispiel: Wieder 'benutze schlüssel auf truhe' -> Spielende
    if verb == "benutze" and len(words) == 4 and words[2] == "auf":
        target = words[3]
        if target == "truhe" and current_room == "turmzimmer":
            # Endgültiges Spielende
            message = (
                "Du hast das letzte Rätsel gelöst! "
                "Ein helles Licht blendet dich ... Du hast das Spiel gewonnen!"
            )
            return True, message, None, True

    # Kein Puzzle erkannt
    return False, "", None, False