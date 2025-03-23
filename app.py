from flask import Flask, render_template, request, redirect, session, url_for

# Level-Daten
import game_data.level1_data
import game_data.level2_data

# Hier liegt die allgemeine Befehlsverarbeitung
from game_logic.commands import process_command

app = Flask(__name__)
app.secret_key = 'dein_geheimer_schlüssel'


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

    level = session['level']
    rooms, items, npcs = get_level_data(level)
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

    return render_template('index.html', description=description, message="")


@app.route('/command', methods=['POST'])
def handle_command():
    command_text = request.form.get('command', '').lower().strip()
    session['command_count'] = session.get('command_count', 0) + 1

    level = session['level']
    rooms, items, npcs = get_level_data(level)

    # process_command gibt uns den Text zurück, der angezeigt werden soll,
    # und ggf. ob wir das Level wechseln oder das Spiel beenden wollen.
    message, new_level, end_game = process_command(
        command_text, session, rooms, items, npcs
    )

    if new_level is not None:
        session['level'] = new_level
        # Raum zurücksetzen, Inventar leeren etc., falls du das pro Level willst
        session['current_room'] = 'start'
        session['inventory'] = []
        # ... oder nur selektiv zurücksetzen

    if end_game:
        return redirect(url_for('endgame'))
    
    current_room = session['current_room']
    description = rooms[current_room]['description']

    items_in_room = [i for i, data in items.items() if data['location'] == current_room]
    if items_in_room:
        description += "\n\nGegenstände hier: " + ", ".join(items_in_room)

    npcs_in_room = [n for n, data in npcs.items() if data['location'] == current_room]
    if npcs_in_room:
        description += "\n\nDu siehst hier: " + ", ".join(npcs_in_room)

    return render_template('index.html', description=description, message=message)


@app.route('/end')
def endgame():
    command_count = session.get('command_count', 0)
    return render_template('end.html', command_count=command_count)


@app.route('/restart', methods=['POST'])
def restart():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)