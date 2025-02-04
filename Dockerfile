FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

RUN pip install --upgrade gigachat langgraph validators aiogram_calendar salute-speech

RUN pip install langchain-gigachat

COPY . /app

RUN sh -c "pip install protobuf==3.19.4 && cp ./builder.py /usr/local/lib/python3.10/site-packages/google/protobuf/internal/"
