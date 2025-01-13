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
        character_data["Spells"] = dict(sorted(character_data["Spells"].items(), key=lambda x: int(x[0].split()[1])))
        return render_template('character_sheet.html', data=character_data)

        #return jsonify(character_data)
    else:
        return jsonify({"error": "No character data found."}), 404


@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    try:
        # Получаем данные из запроса
        data = request.json  # Пример данных: {"path": "Spells.Level 1.spells[0].checked", "value": true}
        if not data or "path" not in data or "value" not in data:
            return jsonify({"error": "Invalid data format"}), 400
        
        # Получение пути и значения
        path = data["path"]  # Путь к полю, например, "Spells.Level 1.spells[0].checked"
        value = data["value"]  # Новое значение для чекбокса

        # Получаем документ из Firestore
        doc_ref = db.collection("character_data").document("main")
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Character data not found"}), 404

        # Получаем текущие данные документа
        character_data = doc.to_dict()

        # Обновляем поле по указанному пути
        keys = path.split(".")  # Разделяем путь
        sub_data = character_data
        for key in keys[:-1]:  # Проходим по всем, кроме последнего ключа
            if key not in sub_data:
                return jsonify({"error": f"Path not found: {path}"}), 400
            sub_data = sub_data[key]
        
        # Устанавливаем значение чекбокса
        final_key = keys[-1]
        sub_data[final_key] = value

        # Обновляем документ в Firestore
        doc_ref.set(character_data)
        
        return jsonify({"status": "success", "updated_path": path, "new_value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)