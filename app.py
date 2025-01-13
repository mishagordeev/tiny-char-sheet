import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

print("Starting application...")

# Инициализация переменной db
db = None

# Получаем строку JSON из переменной окружения
json_key_str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

if json_key_str:
    try:
        # Преобразуем строку JSON в словарь
        json_data = json.loads(json_key_str)
        logging.debug("Successfully parsed JSON.")
        print("Successfully parsed JSON.")

        try:

            cred = credentials.Certificate(json_data)
            firebase_admin.initialize_app(cred)
            logging.debug("Firebase initialized successfully.")
            print("Firebase initialized successfully.")

            # Инициализация Firestore клиента
            db = firestore.client()
            logging.debug("Firestore client initialized successfully.")
            print("Firestore client initialized successfully.")

        except Exception as e:
            logging.error(f"Unexpected error during initialization: {e}")
            print(f"Unexpected error during initialization: {e}")
            raise


    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        print(f"JSONDecodeError: {e}")
        raise


else:
    logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
    print("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

# Flask приложение
app = Flask(__name__)
app.debug = True

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
        logging.error(f"Error fetching document: {e}")
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
        logging.error(f"Error updating document: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/test")
def test():
    return "This is a test route."

if __name__ == "__main__":
    app.run()
