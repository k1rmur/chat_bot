FROM python:3.10

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN pip install --upgrade gigachat langgraph validators aiogram_calendar salute-speech

RUN git clone https://github.com/mmua/salute_speech.git
COPY ./token.py ./salute_speech/src/salute_speech/utils/
COPY ./speech_recognition.py ./salute_speech/src/salute_speech/
RUN pip install ./salute_speech

RUN pip install langgraph-checkpoint==2.1.1 llama-index-embeddings-langchain==0.4.0 llama-index==0.13.0 llama-index-core==0.13.0
RUN pip install pydantic==2.11.7 pydantic_core==2.33.2 langchain==0.3.27 langchain-community==0.3.27 langchain-core==0.3.72
RUN pip install textract==1.5.0
RUN pip install ctranslate2==4.4.0

RUN sh -c "pip install protobuf==3.19.4 && cp ./builder.py /usr/local/lib/python3.10/site-packages/google/protobuf/internal/"