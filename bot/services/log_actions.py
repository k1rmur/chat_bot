import datetime

CSV_LOG_PATH = '/app/logs/stats.csv'


allowed_actions = {
    "menu": 'Навигация по меню',
    "ai": 'Вопрос ИИ',
    "start": 'Начало диалога',
    "protocol": 'Протокол',
}


def log_action(message, action):
    with open(CSV_LOG_PATH, 'a') as file:
        user_id = message.peer_id
        mydate = datetime.datetime.now()

        file.write(",".join([str(user_id), str(mydate), action])+'\n')
