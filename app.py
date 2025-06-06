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
        return render_template('character_sheet.html', data=character_data)

        #return jsonify(character_data)
    else:
        return jsonify({"error": "No character data found."}), 404


@app.route('/update_field', methods=['POST'])
def update_field():
    try:
        # Получаем данные из запроса
        data = request.json  # Пример данных: {"path": "Spells.Level 1.spells[0].checked", "value": true}
        if not data:
            return jsonify({"error": "Invalid data format"}), 400    
        
        doc_ref = db.collection("character_data").document("main")
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Character data not found"}), 404
        
        character_data = doc.to_dict()
        
        field = data["field"]
        value = data["value"]

        current = character_data

        for key in field[:-1]:  # Идём по всем ключам, кроме последнего
            current = current.setdefault(key, {})
        current[field[-1]] = value  # Устанавливаем финальное значение
        
        doc_ref.set(character_data)
        
        return jsonify({"status": "success", "updated": data})
    except Exception as e:
        import traceback
        traceback.print_exc()  # Выведет полную ошибку в консоль
        return jsonify({"error": str(e)}), 500

@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    try:
        # Получаем данные из запроса
        data = request.json  # Пример данных: {"path": "Spells.Level 1.spells[0].checked", "value": true}
        if not data or "level" not in data or "used" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        # Получаем документ из Firestore
        doc_ref = db.collection("character_data").document("main")
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Character data not found"}), 404

        # Получаем текущие данные документа
        character_data = doc.to_dict()

        # Проверяем, существует ли нужный уровень заклинаний
        level = int(data["level"])
        logging.info(level)
        # if slots not in character_data["Spells"]:
        #     return jsonify({"error": f"Spell level '{level}' not found"}), 404

        # Получаем список заклинаний
        used = character_data["Spells"]["slots"][level]["used"]
        logging.info(used)

        # Проверяем, существует ли заклинание с таким индексом
        # index = int(data["index"])
        # if not (0 <= index < len(checkboxes)):
        #     return jsonify({"error": "Spell index out of range"}), 400

        # Устанавливаем новое значение чекбокса
        used = data["used"]
        logging.info(used)
        logging.info(character_data["Spells"]["slots"][level]["used"])
        character_data["Spells"]["slots"][level]["used"] = used
        logging.info(character_data["Spells"]["slots"][level]["used"])
        # Обновляем документ в Firestore
        doc_ref.set(character_data)
        
        return jsonify({"status": "success", "updated": data})
    except Exception as e:
        import traceback
        traceback.print_exc()  # Выведет полную ошибку в консоль
        return jsonify({"error": str(e)}), 500

@app.route('/download_json', methods=['GET'])
def download_json():
    try:
        # Получаем данные из Firestore
        doc_ref = db.collection("character_data").document("main")
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Данных нет"}), 404

        return jsonify(doc.to_dict())  # Отправляем JSON в ответе

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/upload_json', methods=['POST'])
def upload_json():
    try:
        data = request.json  # Получаем JSON-данные из запроса

        if not data:
            return jsonify({"error": "Нет данных"}), 400

        # Сохраняем в Firestore
        doc_ref = db.collection("character_data").document("main")
        doc_ref.set(data)

        return jsonify({"status": "success", "message": "Данные успешно записаны в базу"})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500    

if __name__ == '__main__':
    app.run(debug=True)