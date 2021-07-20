import requests
import logging
import time
import telegram
from dotenv import load_dotenv
import os


def main():
    logging.warning("БОТ ЗАПУЩЕН!")

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

    times_exceptions_appear = 0

    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=91,
                params=payload
            )
            response.raise_for_status()
            review = response.json()
            if review["status"] == "timeout":
                timestamp = review["timestamp_to_request"]
            elif review["status"] == "found":
                timestamp = review["last_attempt_timestamp"]
                chat_id = os.getenv("TG_CHAT_ID")
                last_new_attempt = review['new_attempts'][0]
                work_name = last_new_attempt['lesson_title']
                work_url = last_new_attempt['lesson_url']
                if last_new_attempt["is_negative"]:
                    final_message = "К сожалению, в работе нашлись ошибки."
                else:
                    final_message = "Преподавателю все понравилось,"
                    + "можно приступать к следующему уроку!"
                bot.send_message(
                    chat_id,
                    text=f"""Преподаватель проверил работу:
                    '{work_name}'
                    dvmn.org{work_url}
                    {final_message}"""
                    )
        except requests.exceptions.ConnectionError:
            if times_exceptions_appear > 10:
                time.sleep(10)
                times_exceptions_appear = 0
            else:
                times_exceptions_appear += 1
        except requests.exceptions.ReadTimeout:
            continue

if __name__ == '__main__':
    main()
