from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

# Load JSON data from file
def load_character_data():
    with open('character_data.json', 'r') as file:
        return json.load(file)

# Save JSON data to file
def save_character_data(data):
    with open('character_data.json', 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def character_sheet():
    character_data = load_character_data()
    character_data["Spells"] = dict(sorted(character_data["Spells"].items(), key=lambda x: int(x[0].split()[1])))
    return render_template('character_sheet.html', data=character_data)

@app.route('/data')
def get_character_data():
    character_data = load_character_data()
    character_data["Spells"] = dict(sorted(character_data["Spells"].items(), key=lambda x: int(x[0].split()[1])))
    return jsonify(character_data)

@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    data = load_character_data()
    spell_level = request.json.get('level')
    checkbox_index = request.json.get('checkbox_index')
    checked = request.json.get('checked')
    
    # Update the checkbox state in the data
    if spell_level in data['Spells']:
        if 'checkboxes_state' not in data['Spells'][spell_level]:
            data['Spells'][spell_level]['checkboxes_state'] = [False] * data['Spells'][spell_level]['checkboxes']
        data['Spells'][spell_level]['checkboxes_state'][checkbox_index] = checked

    save_character_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)