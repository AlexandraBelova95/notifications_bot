import requests
import time
import telegram
from dotenv import load_dotenv
import os


def main():
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
            if response.json()["status"] == "timeout":
                timestamp = response.json()["timestamp_to_request"]
            elif response.json()["status"]== "found":
                timestamp = response.json()["last_attempt_timestamp"]
                chat_id = os.getenv("TG_CHAT_ID")
                last_new_attempt = response.json()['new_attempts'][0]
                work_name = last_new_attempt['lesson_title']
                work_url = last_new_attempt['lesson_url']
                bot.send_message(
                    chat_id, 
                    text="Преподаватель проверил работу\n"+
                    f"'{work_name}'\ndvmn.org{work_url}"
                    )
                if last_new_attempt["is_negative"]:
                    text = "К сожалению, в работе нашлись ошибки"
                    bot.send_message(chat_id, text=text)
                elif last_new_attempt["is_negative"]:
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

if __name__ == '__main__':
    main()