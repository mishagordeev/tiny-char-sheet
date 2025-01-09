import os
import json
import firebase_admin
from firebase_admin import credentials
from io import StringIO
from flask import Flask, jsonify, request
import logging
from google.cloud import firestore

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
print("Starting the Flask app...")

# Инициализация переменной db
db = None

# Получаем строку JSON из переменной окружения
json_key_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
logging.debug(f"GOOGLE_APPLICATION_CREDENTIALS: {json_key_str}")

# Проверяем, что переменная окружения установлена
if json_key_str:
    try:
        # Преобразуем строку в объект виртуального файла
        json_file = StringIO(json_key_str)
        
        # Загружаем учетные данные из виртуального файла
        cred = credentials.Certificate(json.load(json_file))
        firebase_admin.initialize_app(cred)
        logging.debug("Firebase initialized successfully.")
        
        # Инициализируем Firestore клиента
        
        try:
            db = firestore.Client.from_service_account_info(json.loads(json_key_str))
            print("Firestore client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Firestore client: {e}")
        logging.debug("Firestore client initialized successfully.")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
    except Exception as e:
        print(f"Unexpected error during initialization: {e}")
else:
    logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

# Инициализация Flask приложения
app = Flask(__name__)

# Коллекция, где будут храниться данные
COLLECTION_NAME = "character_data"

@app.route('/')
def character_sheet():
    if db is None:
        return jsonify({"error": "Database is not initialized."}), 500
    try:
        doc_ref = db.collection(COLLECTION_NAME).document('main')
        doc = doc_ref.get()
        if doc.exists:
            character_data = doc.to_dict()
            return jsonify(character_data)
        else:
            return jsonify({"error": "No character data found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update', methods=['POST'])
def update_character_sheet():
    if db is None:
        return jsonify({"error": "Database is not initialized."}), 500
    try:
        character_data = request.json
        doc_ref = db.collection(COLLECTION_NAME).document('main')
        doc_ref.set(character_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test")
def test():
    return "This is a test route."

if __name__ == "__main__":
    app.run()
