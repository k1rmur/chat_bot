# Телеграм-бот ФАВР

## Установка и развертывание
```
pip install --ignore-installed -r requirements.txt
```
```
mkdir .env
```
```
В .env добавить: 
BOT_TOKEN="API telegram bot"
CREDENTIALS="Authorization data for GigaChat API"
```
```
sudo python3 make_embeddings.py
```
```
sudo python3 get_bot.py
```
