from flask import Flask, render_template, request, redirect, session, url_for
import copy

# Level-Daten
import game_data.level1_data
import game_data.level2_data

# Hier liegt die allgemeine Befehlsverarbeitung
from game_logic.commands import process_command

app = Flask(__name__)
app.secret_key = 'dein_geheimer_schlüssel'

final_level = 3

def get_level_data(level):
    """Lädt die passenden Räume, Items, NPCs für das gegebene Level."""
    if level == 1:
        return (
            game_data.level1_data.rooms_level1,
            game_data.level1_data.items_level1,
            game_data.level1_data.npcs_level1
        )
    elif level == 2:
        return (
            game_data.level2_data.rooms_level2,
            game_data.level2_data.items_level2,
            game_data.level2_data.npcs_level2
        )
    return ({}, {}, {})


@app.route('/')
def index():
    if 'level' not in session:
        session['level'] = 1
    if 'current_room' not in session:
        session['current_room'] = 'start'
    if 'inventory' not in session:
        session['inventory'] = []
    if 'command_count' not in session:
        session['command_count'] = 0
    if 'endnote' not in session:
        session['endnote'] = ''

    level = session['level']
    # Falls noch keine Level-Daten in der Session gespeichert sind, initialisiere sie
    if 'rooms' not in session or 'items' not in session or 'npcs' not in session:
        rooms, items, npcs = copy.deepcopy(get_level_data(level))
        session['rooms'] = rooms
        session['items'] = items
        session['npcs'] = npcs
    else:
        rooms = session['rooms']
        items = session['items']
        npcs = session['npcs']

    current_room = session['current_room']

    # Beschreibung aus dem passenden Dictionary holen
    description = rooms[current_room]['description']
    # Gegenstände und NPCs, die hier liegen
    items_in_room = [i for i, data in items.items() if data['location'] == current_room]
    if items_in_room:
        description += "\n\nGegenstände hier: " + ", ".join(items_in_room)
    npcs_in_room = [n for n, data in npcs.items() if data['location'] == current_room]
    if npcs_in_room:
        description += "\n\nDu siehst hier: " + ", ".join(npcs_in_room)

    return render_template('index.html', description=description, message="", error = "", image = rooms[current_room]['image'], room = current_room)


@app.route('/command', methods=['POST'])
def handle_command():
    command_text = request.form.get('command', '').lower().strip()
    session['command_count'] = session.get('command_count', 0) + 1

    level = session['level']
    # Lade die Level-Daten aus der Session, falls vorhanden, ansonsten initialisiere sie
    if 'rooms' not in session or 'items' not in session or 'npcs' not in session:
        rooms, items, npcs = copy.deepcopy(get_level_data(level))
    else:
        rooms = session['rooms']
        items = session['items']
        npcs = session['npcs']

    

    # process_command gibt uns den Text zurück, der angezeigt werden soll,
    # und ggf. ob wir das Level wechseln oder das Spiel beenden wollen.
    message, error, new_level, end_game, won_game = process_command(
        command_text, session, rooms, items, npcs
    )
    session ['endnote'] = message

    if new_level is not None:
        session['level'] = new_level
        # Raum zurücksetzen, Inventar leeren etc., falls du das pro Level willst
        session['current_room'] = 'start'
        session['inventory'] = []
        # ... oder nur selektiv zurücksetzen
        session.pop('rooms', None)
        session.pop('items', None)
        session.pop('npcs', None)

    if end_game and won_game:
        return redirect(url_for('endgame'))
    elif end_game:
        return redirect(url_for('defeat'))
    
    session['rooms'] = rooms
    session['items'] = items
    session['npcs'] = npcs

    current_room = session['current_room']
    description = rooms[current_room]['description']

    items_in_room = [i for i, data in items.items() if data['location'] == current_room]
    if items_in_room:
        description += "\n\nGegenstände hier: " + ", ".join(items_in_room)

    npcs_in_room = [n for n, data in npcs.items() if data['location'] == current_room]
    if npcs_in_room:
        description += "\n\nDu siehst hier: " + ", ".join(npcs_in_room)

    return render_template('index.html', description=description, message=message, error = error, image = rooms[current_room]['image'], room = current_room)


@app.route('/end')
def endgame():
    command_count = session.get('command_count', 0)

    if session['level'] == final_level:
        return render_template('end.html', command_count=command_count, endnote = session.get('endnote', ""))
    else : 
        return render_template('end_of_level.html', command_count=command_count, endnote = session.get('endnote', ""))

@app.route('/defeat')
def defeat():
    return render_template('defeat.html', endnote = session.get('endnote', "Debug"))


@app.route('/restart', methods=['POST'])
def restart():
    session.clear()
    return redirect(url_for('index'))

@app.route('/nextlevel', methods=['POST'])
def nextlevel():
    level = session["level"]
    session.clear()
    session["level"] = level
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)