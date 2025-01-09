from flask import Flask, jsonify, request
import os
from google.cloud import firestore

# Загружаем JSON ключ из переменной окружения
import json
from io import StringIO

json_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {json_key}")
if json_key:
    key_file = StringIO(json_key)  # Преобразуем строку в файловый объект
    db = firestore.Client.from_service_account_json(key_file)
else:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set")

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