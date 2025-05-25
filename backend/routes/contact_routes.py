from datetime import datetime
import re
from flask import Blueprint, request, jsonify
import pytz

contact_bp = Blueprint('contact_bp', __name__)

@contact_bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    subject = data.get('subject')
    text = data.get('text')

    if not all([username, email, subject, text]):
        return jsonify({"error": "Wszystkie pola są wymagane."}), 400

    number = 1
    try:
        with open("contact.txt", "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(r'^(\d+)\.', content, re.MULTILINE)
            if matches:
                number = int(matches[-1]) + 1
    except FileNotFoundError:
        pass

    now = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%d-%m-%Y %H:%M:%S")
    message = (
        f"{number}. {now}\n"
        f"Nazwa użytkownika: {username}\n"
        f"Email: {email}\n"
        f"Temat: {subject}\n"
        f"Wiadomość: {text}\n\n"
    )

    with open("contact.txt", "a", encoding="utf-8") as f:
        f.write(message)

    return jsonify({"message": "Wiadomość została wysłana."}), 200