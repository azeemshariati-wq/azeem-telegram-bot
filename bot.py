
import os
import requests
import phonenumbers
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

def send_message(chat_id, text):
    if TOKEN:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15
        )

def send_location(chat_id, lat, lon):
    if TOKEN:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendLocation",
            json={
                "chat_id": chat_id,
                "latitude": lat,
                "longitude": lon
            },
            timeout=15
        )

@app.route("/", methods=["GET"])
def home():
    return "Telegram bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return "OK"

    if text == "/start":
        send_message(
            chat_id,
            "سلام! 👋\n"
            "شماره را با + و کد کشور بفرست.\n"
            "برای دیدن موقعیت روی نقشه، خودت موقعیت را از تلگرام بفرست."
        )

    elif text.startswith("+"):
        try:
            number = phonenumbers.parse(text, None)
            country = phonenumbers.region_code_for_number(number)
            valid = phonenumbers.is_valid_number(number)
            send_message(
                chat_id,
                f"کشور: {country or 'نامشخص'}\n"
                f"قالب شماره: {'معتبر' if valid else 'نامعتبر یا ناقص'}\n"
                "موقعیت فعلی از روی شماره قابل تعیین نیست."
            )
        except Exception:
            send_message(chat_id, "شماره را با کد کشور بفرست؛ مثل +937XXXXXXXX.")

    elif message.get("location"):
        loc = message["location"]
        lat = loc["latitude"]
        lon = loc["longitude"]
        send_message(chat_id, "موقعیت دریافت شد؛ این نقطه را روی نقشه ببین:")
        send_location(chat_id, lat, lon)
        send_message(
            chat_id,
            f"نقشه: https://maps.google.com/?q={lat},{lon}"
        )

    elif text:
        send_message(
            chat_id,
            "برای شروع /start را بفرست.\n"
            "برای موقعیت، از 📎 و سپس Location استفاده کن."
        )

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
