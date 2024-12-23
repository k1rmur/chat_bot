import datetime

CSV_LOG_PATH = "/app/logs/stats.csv"


allowed_actions = {
    "menu": "Навигация по меню",
    "ai": "Вопрос ИИ",
    "start": "Начало диалога",
    "protocol": "Протокол",
}


def log_action(message, action):
    try:
        with open(CSV_LOG_PATH, "a") as file:
            user_id = message.from_user.id
            username = message.from_user.username
            if username is None:
                username = "Скрыт"
            mydate = datetime.datetime.now()

            file.write(",".join([str(user_id), username, str(mydate), action]) + "\n")
    except Exception as e:
        print(e)
