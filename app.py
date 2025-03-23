from flask import Flask, render_template, request, redirect, session, url_for
import assets.constants
app = Flask(__name__)
app.secret_key = 'dein_geheimer_schlüssel'  # Bitte ersetzen durch einen eigenen zufälligen Wert!

rooms = assets.constants.rooms
items = assets.constants.items
npcs = assets.constants.npcs

@app.route('/')
def index():
    # Session initialisieren
    if 'current_room' not in session:
        session['current_room'] = 'start'
    if 'inventory' not in session:
        session['inventory'] = []
    if 'chest_open' not in session:
        session['chest_open'] = False  # Status der Truhe
    if 'got_code' not in session:
        session['got_code'] = False    # Hat der Spieler den Code erfahren?
    if 'command_count' not in session:
        session['command_count'] = 0   # Zählt die Befehle

    current_room = session['current_room']
    description = rooms[current_room]['description']

    # Hinweis, welche Gegenstände hier liegen
    items_in_room = [
        i for i, data in items.items()
        if data['location'] == current_room
    ]
    if items_in_room:
        description += "\n\nGegenstände hier: " + ", ".join(items_in_room)

    # Hinweis, ob ein NPC hier ist
    npcs_in_room = [
        n for n, data in npcs.items()
        if data['location'] == current_room
    ]
    if npcs_in_room:
        description += "\n\nDu siehst hier: " + ", ".join(npcs_in_room)

    return render_template('index.html', description=description, message="")

@app.route('/command', methods=['POST'])
def process_command():
    command = request.form.get('command', '').lower().strip()
    # Bei jedem Befehl den Zähler erhöhen
    session['command_count'] = session.get('command_count', 0) + 1

    current_room = session.get('current_room', 'start')
    inventory = session.get('inventory', [])
    chest_open = session.get('chest_open', False)
    got_code = session.get('got_code', False)

    # Räume, Items, NPCs
    room = rooms.get(current_room, {})
    
    # Wir teilen den Befehl in bis zu drei Teile auf
    # Beispiel: "nimm schlüssel" -> verb = "nimm", obj = "schlüssel"
    words = command.split()
    verb = words[0] if len(words) > 0 else ""
    obj = words[1] if len(words) > 1 else ""

    message = ""

    # 1) BEWEGUNG prüfen
    if verb in room:
        # Gültige Bewegung
        session['current_room'] = room[verb]
        return redirect(url_for('index'))

    # 2) SPEZIELLE BEFEHLE
    if verb == "nimm":
        # 'nimm <gegenstand>'
        if obj in items and items[obj]['location'] == current_room and items[obj]['pickupable']:
            # Gegenstand aufnehmen
            inventory.append(obj)
            session['inventory'] = inventory
            items[obj]['location'] = "inventory"
            message = f"Du hebst den {obj} auf."
        else:
            message = f"Du kannst '{obj}' hier nicht aufnehmen."
    
    elif verb == "untersuche":
        # 'untersuche <objekt>'
        if obj in items:
            if items[obj]['location'] == current_room or items[obj]['location'] == "inventory":
                message = f"Du untersuchst den {obj}: {items[obj]['description']}"
            else:
                message = f"Hier ist kein '{obj}' zum Untersuchen."
        elif obj in npcs:
            # NPC untersuchen
            if npcs[obj]['location'] == current_room:
                message = f"Du betrachtest den {obj} genauer. Er wirkt erschöpft, aber freundlich."
            else:
                message = f"'{obj}' ist nicht hier."
        elif obj == "truhe" and current_room == "schuppen":
            if chest_open:
                message = "Die Truhe ist bereits offen."
            else:
                message = "Die Truhe ist verschlossen. Du brauchst den richtigen Code, um sie zu öffnen."
        else:
            message = f"Du findest nichts Interessantes zu '{obj}'."

    elif verb == "rede":
        # 'rede mit <person>'
        if len(words) >= 3 and words[1] == "mit":
            person = words[2]
            if person in npcs and npcs[person]['location'] == current_room:
                # Zeige Dialog
                dialogue_lines = npcs[person]['dialogue']
                message = "\n".join(dialogue_lines)
                # Der Spieler hat jetzt den Code erfahren
                session['got_code'] = True
            else:
                message = f"'{person}' ist nicht hier."
        else:
            message = "Mit wem möchtest du reden? Beispiel: 'rede mit wanderer'"

    elif verb == "benutze":
        # 'benutze <gegenstand> auf <ziel>'
        if obj in inventory:
            if len(words) == 4 and words[2] == "auf":
                target = words[3]
                if target == "truhe" and current_room == "schuppen":
                    # Braucht zusätzlich den Code
                    if got_code:
                        # Truhe öffnen -> Spielende
                        session['chest_open'] = True
                        # Leite auf Endseite weiter
                        return redirect(url_for('endgame'))
                    else:
                        message = (
                            "Du hast zwar den Schlüssel, aber du kennst den Code nicht. "
                            "Vielleicht solltest du mit jemandem reden?"
                        )
                else:
                    message = f"Du kannst '{obj}' hier nicht auf '{target}' benutzen."
            else:
                message = f"Wie möchtest du '{obj}' benutzen? Zum Beispiel: 'benutze schlüssel auf truhe'"
        else:
            message = f"Du hast '{obj}' nicht im Inventar."

    elif verb == "inventar":
        # Liste alle Gegenstände im Inventar
        if inventory:
            message = "Dein Inventar enthält: " + ", ".join(inventory)
        else:
            message = "Dein Inventar ist leer."

    else:
        # Ungültiger Befehl oder falscher Raum-Befehl
        possible_commands = [key for key in room.keys() if key != "description"]
        # Zusätzliche Hilfsbefehle anfügen
        possible_commands += ["nimm <item>", "untersuche <objekt>", "rede mit <person>", 
                              "benutze <item> auf <ziel>", "inventar"]
        message = "Ungültiger Befehl. Versuche es mit: " + ", ".join(possible_commands)

    description = room['description']

    # Gegenstände im Raum angeben
    items_in_room = [
        i for i, data in items.items()
        if data['location'] == current_room
    ]
    if items_in_room:
        description += "\n\nGegenstände hier: " + ", ".join(items_in_room)

    # NPCs im Raum angeben
    npcs_in_room = [
        n for n, data in npcs.items()
        if data['location'] == current_room
    ]
    if npcs_in_room:
        description += "\n\nDu siehst hier: " + ", ".join(npcs_in_room)

    return render_template('index.html', description=description, message=message)

@app.route('/end')
def endgame():
    # Anzahl der Befehle aus der Session holen
    command_count = session.get('command_count', 0)
    return render_template('end.html', command_count=command_count)

@app.route('/restart', methods=['POST'])
def restart():
    # Session zurücksetzen und von vorne starten
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)