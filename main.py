from flask import Flask, request, jsonify
import os
import openai
import requests

app = Flask(__name__)

# Настройки: убедись, что переменные окружения настроены на Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BITRIX24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK")

@app.route("/")
def home():
    return "Bitrix24 Chatbot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Получен запрос:", data)  # Логируем входящий запрос

    message = data.get("data", {}).get("MESSAGE", "").lower()
    print("Обрабатываем сообщение:", message)

    if "стоимость" in message:
        response_text = "Я передам ваш запрос менеджеру, он скоро свяжется с вами."
        print("Обнаружено ключевое слово 'стоимость'. Передаю менеджеру.")
    else:
        openai.api_key = OPENAI_API_KEY
        try:
            print("Отправляю запрос в OpenAI...")
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты - помощник компании по логистике."},
                    {"role": "user", "content": message}
                ]
            )
            response_text = completion["choices"][0]["message"]["content"].strip()
            print("Ответ от OpenAI:", response_text)
        except Exception as e:
            response_text = "Извините, возникла ошибка при обработке вашего запроса."
            print("Ошибка OpenAI:", e)

    # Отправка ответа через Bitrix24 API
    url = f"{BITRIX24_WEBHOOK}/im.message.add"
    payload = {
        "DIALOG_ID": data.get("data", {}).get("DIALOG_ID"),
        "MESSAGE": response_text
    }
    try:
        print("Отправляю ответ в Bitrix24 по URL:", url)
        requests.post(url, json=payload)
    except Exception as e:
        print("Ошибка при отправке в Bitrix24:", e)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
