from flask import Flask, jsonify, request
import os
import json
import firebase_admin
from firebase_admin import credentials

json_key_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Проверяем, что переменная окружения установлена
if json_key_str:
    try:
        # Преобразуем строку JSON в объект Python (словарь)
        json_key = json.loads(json_key_str)
        
        # Используем полученные данные для инициализации Firebase
        cred = credentials.Certificate(json_key)
        firebase_admin.initialize_app(cred)
        print("Firebase app initialized successfully.")
    except json.JSONDecodeError:
        print("Error decoding JSON from the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
else:
    print("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

# Инициализация Flask приложения
app = Flask(__name__)

# Коллекция, где будут храниться данные
COLLECTION_NAME = "character_data"

@app.route('/')
def character_sheet():
    doc_ref = db.collection(COLLECTION_NAME).document('main')
    doc = doc_ref.get()
    if doc.exists:
        character_data = doc.to_dict()
        return jsonify(character_data)
    else:
        return jsonify({"error": "No character data found."}), 404

@app.route('/update', methods=['POST'])
def update_character_sheet():
    try:
        character_data = request.json
        doc_ref = db.collection(COLLECTION_NAME).document('main')
        doc_ref.set(character_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)