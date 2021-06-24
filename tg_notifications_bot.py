import requests
import time
import telegram
from dotenv import load_dotenv
import os

load_dotenv()

devman_token = os.getenv("DEVMAN_TOKEN")
telegram_token = os.getenv("TELEGRAM_TOKEN")

url = 'https://dvmn.org/api/long_polling/'

bot = telegram.Bot(token=telegram_token)

timestamp = time.time()

headers = {
    "Authorization": devman_token
    }
payload = {
    timestamp: timestamp
    }

times_exceptions_appear = 0;

while True:
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=91,
            params=payload
        )
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] == "timeout":
            timestamp = response_json["timestamp_to_request"]
        elif response_json["status"] == "found":
            timestamp = response_json["last_attempt_timestamp"]
            chat_id = os.getenv("TG_CHAT_ID")
            bot.send_message(chat_id, text="Преподаватель проверил работу")
            work_name = response_json['new_attempts'][0]['lesson_title']
            bot.send_message(chat_id, text=f"'{work_name}'")
            work_url = response_json['new_attempts'][0]['lesson_url']
            bot.send_message(chat_id, text=f"dvmn.org{work_url}")
            if response_json["new_attempts"][0]["is_negative"]:
                text = "К сожалению, в работе нашлись ошибки"
                bot.send_message(chat_id, text=text)
            elif not response_json["new_attempts"][0]["is_negative"]:
                text = "Преподавателю все понравилось,"
                + "можно приступать к следующему уроку!"
                bot.send_message(chat_id, text=text)
    except (
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectionError
    ):
        if times_exceptions_appear > 10:
            time.sleep(10)
            times_exceptions_appear = 0
        else: 
            times_exceptions_appear+=1
