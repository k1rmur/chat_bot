import csv
from datetime import datetime


CSV_LOG_PATH = "/app/logs/stats.csv"


allowed_actions = {
    "menu": "Навигация по меню",
    "ai": "Вопрос ИИ",
    "start": "Начало диалога",
    "protocol": "Протокол",
}


def log_action(message, action, answer=None):
    try:
        with open(CSV_LOG_PATH, "a") as file:
            writer = csv.writer(file)
            user_id = message.from_user.id
            username = message.from_user.username
            if username is None:
                username = "Скрыт"
            mydate = datetime.now()

            if action == "Вопрос ИИ" and answer:
                writer.writerow([str(user_id), username, str(mydate), message.text])
            else:
                writer.writerow([str(user_id), username, str(mydate), action])
    except Exception as e:
        print(e)