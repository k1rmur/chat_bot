FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

RUN pip install --upgrade gigachat langgraph validators aiogram_calendar salute-speech

RUN git clone https://github.com/mmua/salute_speech.git

COPY ./token.py ./salute_speech/src/salute_speech/utils/

COPY ./speech_recognition.py ./salute_speech/src/salute_speech/

RUN pip install ./salute_speech

RUN pip install --upgrade langgraph-checkpoint

RUN pip install -U llama-index-embeddings-langchain llama-index llama-index-core langchain langchain-core langchain_community

COPY . /app

RUN sh -c "pip install protobuf==3.19.4 && cp ./builder.py /usr/local/lib/python3.10/site-packages/google/protobuf/internal/"
