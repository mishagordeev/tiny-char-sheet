import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request, render_template
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

print("Starting application...")

# Инициализация переменной db
# db = None

# Получаем строку JSON из переменной окружения
# json_key_str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

service_account = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Инициализация приложения Firebase
if service_account:
    cred = credentials.Certificate(json.loads(service_account))
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("MY_CREDENTIALS environment variable is not set")

# Создание объекта Firestore
db = firestore.client()

# if json_key_str:
#     try:
#         # Преобразуем строку JSON в словарь
#         json_data = json.loads(json_key_str)
#         logging.debug("Successfully parsed JSON.")
#         print("Successfully parsed JSON.")

#         try:
#             cred = credentials.Certificate(json_data)
#             firebase_admin.initialize_app(cred)
#             logging.debug("Firebase initialized successfully.")
#             print("Firebase initialized successfully.")

#             # Инициализация Firestore клиента
#             db = firestore.client()
#             logging.debug("Firestore client initialized successfully.")
#             print("Firestore client initialized successfully.")

#         except Exception as e:
#             logging.error(f"Unexpected error during initialization: {e}")
#             print(f"Unexpected error during initialization: {e}")
#             raise

#     except json.JSONDecodeError as e:
#         logging.error(f"JSONDecodeError: {e}")
#         print(f"JSONDecodeError: {e}")
#         raise

# else:
#     logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
#     print("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

# Flask приложение
app = Flask(__name__)
app.debug = True

COLLECTION_NAME = "character_data"


app = Flask(__name__)

@app.route('/')
def character_sheet():
    doc_ref = db.collection("character_data").document("main")
    doc = doc_ref.get()
    if doc.exists:
        character_data = doc.to_dict()
        return jsonify(character_data)
    else:
        return jsonify({"error": "No character data found."}), 404


@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    try:
        data = request.json  # Получить JSON-данные из запроса
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Обновляем Firestore
        doc_ref = db.collection("character_data").document("main")
        doc_ref.update(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)