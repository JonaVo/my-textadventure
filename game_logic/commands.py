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
    inventory = session_data.get('inventory', {})

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
    if verb in rooms[current_room].get("commands", {}):
        next_room = rooms[current_room]["commands"][verb]

        #checkt ob der nächste Raum ein Schloss hat und verschlossen ist
        if "locked" in rooms[next_room]:
            if rooms[next_room]["locked"]:

                #checkt ob der User den Schlüssel im inventar hat
                if "key" in rooms[next_room]:

                    inventory = session['inventory']
                    item_names = [item_dict["name"] for item_dict in inventory.values()]

                    if rooms[next_room]['key'] not in item_names:
                        message = (
                                "Dieser Raum ist noch viel zu gefährlich für dich. Versuch NICHT nocheinmal ihn zu betreten. Es könnte das Letzte sein, was du tust."
                            )
                        session['rooms'][next_room]["locked"] = False
                        return message, error, new_level, end_game, won_game
        
        # wenn ich in einen offenen raum will, von dem ich den key nicht habe, geh ich drauf
        if "key" in rooms[next_room]:
                    if rooms[next_room]['key'] not in session['inventory']:
                        message = (
                                "Du hast einen Raum betreten, den du nicht hättest betreten sollen. "
                                "Du stribst einen furchtbaren Tod."
                            )
                        end_game = True
                        return message, error, new_level, end_game, won_game



        # Normaler Raumwechsel
        session_data['current_room'] = next_room
        message = f"Du gehst nach {verb}."
        return message, error, new_level, end_game, won_game

    # 2) Nimm
    if verb == 'nimm':
        if obj in items and items[obj]['location'] == current_room and items[obj]['pickupable']:

            inventory = session_data['inventory']  # inventory ist ein Dict
            inventory[obj] = items[obj]           # Speichere das Item unter seinem Namen
            session_data['inventory'] = inventory # Zurück in die Session



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
                        message += (
                            "\n\nDer Mechaniker mustert dich: "
                            "»Du hast ja schon die Waffe! "
                            "Verschwende keine Zeit und erledige das Monster!«"
                        )
                    else:
                        # Prüfen, ob alle benötigten Teile im Inventar sind
                        # (da inventory ein Dict ist, fragen wir einfach nach den Keys)
                        if all(teil in inventory for teil in benoetigte_teile):
                            session_data['waffe_fertig'] = True

                            # Entferne die Teile aus dem Inventar-Dict
                            for teil in benoetigte_teile:
                                del inventory[teil]

                            # Nimm das existierende Waffe-Item aus items und lege es ins Inventar
                            items["waffe"]["location"] = "inventory"
                            inventory["waffe"] = items["waffe"]

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
        # Spieler muss "benutze <item> für <ziel>" eingeben
        if len(words) == 4 and words[2] == 'für':
            tool = words[1]
            target = words[3]

            #Monster Rätsel
            if target == 'monster' and current_room == 'monsterarena':
                if tool == 'waffe':
                    message = (
                        "Du erschießt das Monster. Es fällt um wie ein Sack und landet in einem dunklen Schacht. "
                        "Du hast das Level beendet!"
                    )
                    end_game = True
                    won_game = True
                    session['level'] = session['level'] +1  # Spielende
                else:
                    message = (
                        "Du hättest lieber deine Waffe benutzen sollen. "
                        "Das Monster kommt langsam auf dich zu. "
                        "Es packt dich und frisst dich mit einem Happen auf."
                    )
                    end_game = True
                return message, error, new_level, end_game, won_game

            # Altes Truhenrätsel: In Raum 'schuppen', 'benutze schlüssel für truhe'
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
            # inventory ist ein dict: {"schlüssel": {..}, "stahlrohr": {..}, ...}
            item_names = [item_obj["name"] for item_obj in inventory.values()]
            message = "Dein Inventar enthält: " + ", ".join(item_names)
        else:
            message = "Dein Inventar ist leer."
        return message, error, new_level, end_game, won_game

    # 7) Ungültiger Befehl
    possible_commands = list(rooms[current_room].get("commands", {}).keys())
    possible_commands += ["nimm <item>", "untersuche <objekt>", "rede mit <person>", "benutze <item> für <ziel>", "inventar"]
    error = "Ungültiger Befehl. Versuche es mit: " + ", ".join(possible_commands)
    return message, error, new_level, end_game, won_game